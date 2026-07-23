const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");
const {
  createMemoryMedicalHistoryRepository,
  createSqliteMedicalHistoryRepository,
  migrateJsonToRepository,
} = require("../repository.js");

const patientId = "11111111-1111-4111-8111-111111111111";
const encounterId = "22222222-2222-4222-8222-222222222222";

function sampleSubmission(id, extras = {}) {
  return {
    id,
    submissionId: id,
    patientId,
    encounterId,
    schemaVersion: "1.0.0",
    author: "clinician-1",
    createdAt: "2026-07-23T12:00:00.000Z",
    updatedAt: "2026-07-23T12:00:00.000Z",
    submittedAt: "2026-07-23T12:00:00.000Z",
    status: "submitted",
    version: 1,
    etag: `"${id}"`,
    data: { pastMedicalHistory: [] },
    pastMedicalHistory: [],
    ...extras,
  };
}

async function exerciseRepositoryContract(repository) {
  const activation = {
    activationId: "act-1",
    code: "AB12CD",
    status: "active",
    receivedAt: "2026-07-23T12:00:00.000Z",
    expiresAt: "2026-07-23T14:00:00.000Z",
    context: { patientId, encounterId },
  };
  await repository.upsertActivation(activation);
  assert.equal(repository.getActivationByCode("ab12cd").code, "AB12CD");

  const first = sampleSubmission("aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa");
  const second = sampleSubmission("bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb", {
    data: { pastMedicalHistory: ["Asthma"] },
    pastMedicalHistory: ["Asthma"],
    submittedAt: "2026-07-23T12:00:01.000Z",
  });
  await repository.appendSubmission(first);
  await repository.appendSubmission(second);
  assert.equal(repository.findSubmissionById(first.id).id, first.id);
  assert.deepEqual(
    repository.getSubmissionHistory({ patientId, encounterId }).map((row) => row.id),
    [first.id, second.id],
  );

  const legacy = sampleSubmission("cccccccc-cccc-4ccc-8ccc-cccccccccccc", { code: "ZZ99YY" });
  const activationAfter = {
    ...activation,
    status: "submitted",
    submissionId: legacy.id,
    submittedAt: legacy.submittedAt,
  };
  const paired = await repository.submitLegacyWithActivation({
    activation: activationAfter,
    submission: legacy,
  });
  assert.equal(paired.activation.status, "submitted");
  assert.equal(repository.getActivationByCode("AB12CD").submissionId, legacy.id);
  assert.equal(repository.listSubmissions({ code: "zz99yy" }).length, 1);
  assert.equal(repository.ping(), true);
}

test("in-memory and sqlite adapters share repository contract", async () => {
  const memory = createMemoryMedicalHistoryRepository();
  await exerciseRepositoryContract(memory);

  const dataDir = fs.mkdtempSync(path.join(os.tmpdir(), "mh-repo-"));
  try {
    const sqlite = createSqliteMedicalHistoryRepository({ dataDir });
    await exerciseRepositoryContract(sqlite);
    const reopened = createSqliteMedicalHistoryRepository({ dataDir });
    assert.equal(reopened.findSubmissionById("aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa").author, "clinician-1");
    sqlite.close();
    reopened.close();
  } finally {
    fs.rmSync(dataDir, { recursive: true, force: true });
  }
});

test("sqlite migrates activation and submission JSON transactionally", () => {
  const dataDir = fs.mkdtempSync(path.join(os.tmpdir(), "mh-migrate-"));
  try {
    fs.writeFileSync(path.join(dataDir, "activation_sessions.json"), JSON.stringify([
      {
        activationId: "act-legacy",
        code: "LEGACY",
        status: "active",
        receivedAt: "2026-07-01T00:00:00.000Z",
        expiresAt: "2026-07-01T02:00:00.000Z",
        context: { patientId: null, encounterId: null },
      },
    ]));
    fs.writeFileSync(path.join(dataDir, "medical_history_submissions.json"), JSON.stringify([
      sampleSubmission("dddddddd-dddd-4ddd-8ddd-dddddddddddd", { code: "LEGACY" }),
    ]));
    const repository = createSqliteMedicalHistoryRepository({
      dataDir,
      databaseFile: "migrated.sqlite",
    });
    const first = migrateJsonToRepository({ dataDir, repository });
    assert.equal(first.activationsMigrated, 1);
    assert.equal(first.submissionsMigrated, 1);
    const second = migrateJsonToRepository({ dataDir, repository });
    assert.equal(second.activationsMigrated, 0);
    assert.equal(second.submissionsMigrated, 0);
    assert.equal(repository.getActivationByCode("LEGACY").activationId, "act-legacy");
    assert.equal(repository.findSubmissionById("dddddddd-dddd-4ddd-8ddd-dddddddddddd").code, "LEGACY");
    repository.close();
  } finally {
    fs.rmSync(dataDir, { recursive: true, force: true });
  }
});

test("concurrent legacy submits preserve distinct submission rows", async () => {
  const dataDir = fs.mkdtempSync(path.join(os.tmpdir(), "mh-concurrent-"));
  try {
    const repository = createSqliteMedicalHistoryRepository({ dataDir });
    await repository.upsertActivation({
      activationId: "act-c",
      code: "CONCUR",
      status: "active",
      receivedAt: "2026-07-23T12:00:00.000Z",
      expiresAt: "2099-01-01T00:00:00.000Z",
      context: { patientId, encounterId },
    });
    const jobs = Array.from({ length: 8 }, (_, index) => {
      const id = `eeeeeeee-eeee-4eee-8eee-eeeeeeeeee${String(index).padStart(2, "0")}`;
      return repository.submitLegacyWithActivation({
        activation: {
          activationId: "act-c",
          code: "CONCUR",
          status: "submitted",
          submissionId: id,
          submittedAt: `2026-07-23T12:00:0${index}.000Z`,
          context: { patientId, encounterId },
        },
        submission: sampleSubmission(id, {
          submittedAt: `2026-07-23T12:00:0${index}.000Z`,
          code: "CONCUR",
        }),
      });
    });
    await Promise.all(jobs);
    assert.equal(repository.listSubmissions({ code: "CONCUR" }).length, 8);
    repository.close();
  } finally {
    fs.rmSync(dataDir, { recursive: true, force: true });
  }
});
