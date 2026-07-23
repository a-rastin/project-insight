import fs from "node:fs";
import path from "node:path";
import { spawnSync } from "node:child_process";

const SQLITE_SCRIPT = String.raw`
import json
import sqlite3
import sys

db_path, operation, payload = sys.argv[1:4]
connection = sqlite3.connect(db_path)
connection.execute("PRAGMA journal_mode=WAL")
connection.execute("""
CREATE TABLE IF NOT EXISTS assessments (
  assessment_id TEXT PRIMARY KEY,
  resource_json TEXT NOT NULL,
  etag TEXT,
  version INTEGER,
  updated_at TEXT
)
""")
data = json.loads(payload)

if operation == "read":
    rows = connection.execute(
        "SELECT assessment_id, resource_json FROM assessments ORDER BY assessment_id"
    ).fetchall()
    result = {assessment_id: json.loads(resource_json) for assessment_id, resource_json in rows}
elif operation == "get":
    row = connection.execute(
        "SELECT resource_json FROM assessments WHERE assessment_id = ?", (data["assessmentId"],)
    ).fetchone()
    result = json.loads(row[0]) if row else None
elif operation == "insert":
    resource = data["resource"]
    cursor = connection.execute(
        "INSERT OR IGNORE INTO assessments (assessment_id, resource_json, etag, version, updated_at) VALUES (?, ?, ?, ?, ?)",
        (data["assessmentId"], json.dumps(resource), resource.get("etag"), resource.get("version"), resource.get("updatedAt", resource.get("updated_at"))),
    )
    connection.commit()
    result = cursor.rowcount == 1
elif operation == "write":
    connection.execute("BEGIN")
    connection.execute("DELETE FROM assessments")
    for assessment_id, resource in data.items():
        connection.execute(
            "INSERT INTO assessments (assessment_id, resource_json, etag, version, updated_at) VALUES (?, ?, ?, ?, ?)",
            (assessment_id, json.dumps(resource), resource.get("etag"), resource.get("version"), resource.get("updatedAt", resource.get("updated_at"))),
        )
    connection.commit()
    result = True
elif operation == "compare_and_swap":
    resource = data["resource"]
    cursor = connection.execute(
        "UPDATE assessments SET resource_json = ?, etag = ?, version = ?, updated_at = ? WHERE assessment_id = ? AND etag = ?",
        (json.dumps(resource), resource.get("etag"), resource.get("version"), resource.get("updatedAt", resource.get("updated_at")), data["assessmentId"], data["expectedEtag"]),
    )
    connection.commit()
    result = resource if cursor.rowcount == 1 else None
else:
    raise ValueError(f"unsupported SQLite operation: {operation}")

print(json.dumps(result, separators=(",", ":")))
connection.close()
`;

function runSqlite(databaseFile, operation, payload) {
  const result = spawnSync(process.env.PYTHON || "python3", [
    "-c", SQLITE_SCRIPT, databaseFile, operation, JSON.stringify(payload),
  ], { encoding: "utf8" });
  if (result.status !== 0) {
    throw new Error(result.stderr.trim() || "SQLite operation failed");
  }
  return JSON.parse(result.stdout);
}

function clone(value) {
  return JSON.parse(JSON.stringify(value));
}

function assertMap(value) {
  if (!value || typeof value !== "object" || Array.isArray(value)) {
    throw new TypeError("assessment repository state must be an object map");
  }
}

export function createMemoryAssessmentStore(initial = {}) {
  assertMap(initial);
  let state = clone(initial);
  return {
    read() {
      return clone(state);
    },
    write(data) {
      assertMap(data);
      state = clone(data);
      return true;
    },
    get(assessmentId) {
      return state[assessmentId] ? clone(state[assessmentId]) : null;
    },
    insert(resource, assessmentId = resource.assessmentId) {
      if (!assessmentId || Object.hasOwn(state, assessmentId)) return false;
      state[assessmentId] = clone(resource);
      return true;
    },
    update(assessmentId, expectedEtag, transform) {
      const current = state[assessmentId];
      if (!current || current.etag !== expectedEtag) return null;
      const next = transform(clone(current));
      state[assessmentId] = clone(next);
      return clone(next);
    },
  };
}

export function createJsonAssessmentStore({
  dataDir = process.env.SEVERITY_DATA_DIR || path.join(path.dirname(new URL(import.meta.url).pathname), "data"),
  fileName = "assessments.json",
} = {}) {
  if (!dataDir) throw new Error("dataDir is required for the JSON adapter");
  const dataFile = path.join(dataDir, fileName);
  fs.mkdirSync(dataDir, { recursive: true });
  if (!fs.existsSync(dataFile)) fs.writeFileSync(dataFile, JSON.stringify({}, null, 2));

  const read = () => {
    try {
      const parsed = JSON.parse(fs.readFileSync(dataFile, "utf8"));
      return parsed && typeof parsed === "object" && !Array.isArray(parsed) ? parsed : {};
    } catch {
      return {};
    }
  };
  const write = data => {
    assertMap(data);
    fs.writeFileSync(dataFile, JSON.stringify(data, null, 2));
    return true;
  };
  return {
    read,
    write,
    get(assessmentId) {
      const state = read();
      return state[assessmentId] ? clone(state[assessmentId]) : null;
    },
    insert(resource, assessmentId = resource.assessmentId) {
      const state = read();
      if (!assessmentId || Object.hasOwn(state, assessmentId)) return false;
      state[assessmentId] = clone(resource);
      return write(state);
    },
    update(assessmentId, expectedEtag, transform) {
      const state = read();
      const current = state[assessmentId];
      if (!current || current.etag !== expectedEtag) return null;
      const next = transform(clone(current));
      state[assessmentId] = clone(next);
      write(state);
      return clone(next);
    },
  };
}

export function createSqliteAssessmentStore({
  dataDir = process.env.SEVERITY_DATA_DIR || path.join(path.dirname(new URL(import.meta.url).pathname), "data"),
  databaseFile = "assessments.sqlite",
} = {}) {
  fs.mkdirSync(dataDir, { recursive: true });
  const databaseFilePath = path.join(dataDir, databaseFile);

  return {
    read() {
      return runSqlite(databaseFilePath, "read", {});
    },
    write(data) {
      assertMap(data);
      return runSqlite(databaseFilePath, "write", data);
    },
    get(assessmentId) {
      return runSqlite(databaseFilePath, "get", { assessmentId });
    },
    insert(resource, assessmentId = resource.assessmentId) {
      return runSqlite(databaseFilePath, "insert", {
        assessmentId,
        resource,
      });
    },
    update(assessmentId, expectedEtag, transform) {
      const current = this.get(assessmentId);
      if (!current || current.etag !== expectedEtag) return null;
      return this.compareAndSwap(assessmentId, expectedEtag, transform(clone(current)));
    },
    compareAndSwap(assessmentId, expectedEtag, resource) {
      return runSqlite(databaseFilePath, "compare_and_swap", {
        assessmentId,
        expectedEtag,
        resource,
      });
    },
  };
}

export function migrateAssessmentsJson({ sourceFile, store }) {
  if (!sourceFile || !store || typeof store.insert !== "function") {
    throw new TypeError("sourceFile and an insert-capable store are required");
  }
  if (!fs.existsSync(sourceFile)) return 0;
  const parsed = JSON.parse(fs.readFileSync(sourceFile, "utf8"));
  assertMap(parsed);
  let migrated = 0;
  for (const [assessmentId, resource] of Object.entries(parsed)) {
    if (resource && typeof resource === "object" && !Array.isArray(resource) && store.insert(resource, assessmentId)) {
      migrated += 1;
    }
  }
  return migrated;
}
