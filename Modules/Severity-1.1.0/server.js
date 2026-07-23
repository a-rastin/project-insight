import express from "express";
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";
import { AssessmentError, computePanssScores, createSeverityAssessmentModule } from "./severity-assessment.js";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const DEFAULT_DATA_DIR = path.join(__dirname, "data");
const DEFAULT_PORT = 3000;

function clone(value) {
  return JSON.parse(JSON.stringify(value));
}

export function createJsonAssessmentStore({
  dataDir = process.env.SEVERITY_DATA_DIR || DEFAULT_DATA_DIR,
  fileName = "assessments.json"
} = {}) {
  const dataFile = path.join(dataDir, fileName);
  fs.mkdirSync(dataDir, { recursive: true });
  if (!fs.existsSync(dataFile)) {
    fs.writeFileSync(dataFile, JSON.stringify({}, null, 2));
  }

  return {
    read() {
      try {
        const parsed = JSON.parse(fs.readFileSync(dataFile, "utf8"));
        return parsed && typeof parsed === "object" && !Array.isArray(parsed) ? parsed : {};
      } catch (error) {
        console.error("Error reading database:", error);
        return {};
      }
    },
    write(data) {
      try {
        fs.writeFileSync(dataFile, JSON.stringify(data, null, 2));
        return true;
      } catch (error) {
        console.error("Error writing database:", error);
        return false;
      }
    }
  };
}

export function createMemoryAssessmentStore(initial = {}) {
  let state = clone(initial);
  return {
    read() {
      return clone(state);
    },
    write(data) {
      state = clone(data);
      return true;
    }
  };
}

export function createApp({ assessmentStore = createJsonAssessmentStore() } = {}) {
  const app = express();
  const severityAssessments = createSeverityAssessmentModule({ assessmentStore });

  app.use(express.json());
  app.use(express.static(path.join(__dirname, "public")));

  // CORS headers for API-first communication with other modules
  app.use((req, res, next) => {
    res.setHeader("Access-Control-Allow-Origin", "*");
    res.setHeader("Access-Control-Allow-Methods", "GET, PUT, POST, OPTIONS");
    res.setHeader("Access-Control-Allow-Headers", "Content-Type, If-Match");
    if (req.method === "OPTIONS") {
      return res.sendStatus(200);
    }
    next();
  });

  app.post("/api/v1/severity-assessments", (req, res) => {
    try {
      const assessment = severityAssessments.create(req.body);
      res.setHeader("ETag", assessment.etag);
      return res.status(201).json(assessment);
    } catch (error) {
      const status = error instanceof AssessmentError ? error.status : 500;
      return res.status(status).json({ error: error.message });
    }
  });

  app.get("/api/v1/severity-assessments/:assessment_id", (req, res) => {
    const assessment = severityAssessments.read(req.params.assessment_id);
    if (!assessment) return res.status(404).json({ error: "Assessment not found" });
    res.setHeader("ETag", assessment.etag);
    return res.json(assessment);
  });

  app.put("/api/v1/severity-assessments/:assessment_id", (req, res) => {
    try {
      const assessment = severityAssessments.update(req.params.assessment_id, req.body, {
        ifMatch: req.get("if-match")
      });
      if (!assessment) return res.status(404).json({ error: "Assessment not found" });
      res.setHeader("ETag", assessment.etag);
      return res.json(assessment);
    } catch (error) {
      const status = error instanceof AssessmentError ? error.status : 500;
      return res.status(status).json({ error: error.message });
    }
  });

  // Legacy GET api/severity/:patient_code adapter.
  app.get("/api/severity/:patient_code", (req, res) => {
    const { patient_code } = req.params;
    if (!patient_code || patient_code.trim() === "") {
      return res.status(400).json({ error: "Patient code is required" });
    }

    const assessments = assessmentStore.read();
    const assessment = assessments[patient_code];

    if (assessment) {
      return res.json(assessment);
    } else {
      return res.json({
        patient_code,
        status: "pending",
        items: {},
        scores: {
          total: 0,
          positive: 0,
          negative: 0,
          general: 0
        }
      });
    }
  });

  // Legacy PUT api/severity/:patient_code adapter.
  app.put("/api/severity/:patient_code", (req, res) => {
    const { patient_code } = req.params;
    const { status, scores, items } = req.body;

    if (!patient_code || patient_code.trim() === "") {
      return res.status(400).json({ error: "Patient code is required" });
    }

    if (!status || !["completed", "passed"].includes(status)) {
      return res.status(400).json({ error: "Status must be 'completed' or 'passed'" });
    }

    const assessments = assessmentStore.read();

    if (status === "passed") {
      assessments[patient_code] = {
        patient_code,
        status: "in_progress",
        updated_at: new Date().toISOString()
      };
    } else {
      let computedScores;
      try {
        computedScores = computePanssScores(items);
      } catch (error) {
        return res.status(error instanceof AssessmentError ? error.status : 400).json({ error: error.message });
      }
      if (!scores || !["positive", "negative", "general", "total"].every(field => scores[field] === computedScores[field])) {
        return res.status(400).json({ error: "Supplied scores do not match PANSS item responses" });
      }

      assessments[patient_code] = {
        patient_code,
        status: "completed",
        scores: computedScores,
        items: { ...items },
        updated_at: new Date().toISOString()
      };
    }

    if (assessmentStore.write(assessments)) {
      return res.json({ success: true, data: assessments[patient_code] });
    }
    return res.status(500).json({ error: "Failed to write to database" });
  });

  // Fallback to SPA index.html for all other routes to allow standalone client-side routing if needed
  app.get("*", (req, res, next) => {
    if (req.path.startsWith("/api/")) {
      return next();
    }
    res.sendFile(path.join(__dirname, "public", "index.html"));
  });

  return app;
}

export const app = createApp();

function start() {
  const port = process.env.PORT || DEFAULT_PORT;
  app.listen(port, () => {
    console.log("====================================================");
    console.log(" Severity Module is running as a Standalone Web App");
    console.log(` URL: http://localhost:${port}`);
    console.log(" GET API: http://localhost:" + port + "/api/severity/:patient_code");
    console.log(" PUT API: http://localhost:" + port + "/api/severity/:patient_code");
    console.log("====================================================");
  });
}

if (process.argv[1] && path.resolve(process.argv[1]) === __filename) {
  start();
}
