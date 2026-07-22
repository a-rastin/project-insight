const http = require("http");
const fs = require("fs/promises");
const path = require("path");
const crypto = require("crypto");

const PORT = Number(process.env.PORT || 4173);
const ROOT_DIR = __dirname;
const PUBLIC_DIR = path.join(ROOT_DIR, "public");
const DATA_DIR = process.env.MEDICAL_HISTORY_DATA_DIR || path.join(ROOT_DIR, "data");
const SESSIONS_FILE = path.join(DATA_DIR, "activation_sessions.json");
const SUBMISSIONS_FILE = path.join(DATA_DIR, "medical_history_submissions.json");
const SCHEMA_FILE = path.join(DATA_DIR, "medical_history_schema.json");

const COMORBIDITY_OPTIONS = [
  "Diabetes mellitus",
  "Hypertension",
  "Coronary artery disease",
  "Heart failure",
  "Chronic obstructive pulmonary disease",
  "Asthma",
  "Chronic kidney disease",
  "Stroke or TIA",
  "Cancer",
  "Depression",
  "Anxiety disorder",
  "Other"
];

const ANTIPSYCHOTIC_OPTIONS = ["Aripiprazole", "Asenapine", "Brexpiprazole", "Cariprazine", "Chlorpromazine", "Clozapine", "Fluphenazine", "Haloperidol", "Iloperidone", "Lurasidone", "Olanzapine", "Paliperidone", "Perphenazine", "Quetiapine", "Risperidone", "Ziprasidone"];
const CLOZAPINE_CONTRAINDICATION_OPTIONS = ["Severe neutropenia", "Clozapine-induced myocarditis", "Unmanaged seizure disorder"];

const MIME_TYPES = {
  ".html": "text/html; charset=utf-8",
  ".css": "text/css; charset=utf-8",
  ".js": "application/javascript; charset=utf-8",
  ".json": "application/json; charset=utf-8",
  ".svg": "image/svg+xml",
  ".png": "image/png",
  ".ico": "image/x-icon"
};

function isValidCode(code) {
  return typeof code === "string" && /^[A-Za-z0-9]{6}$/.test(code.trim());
}

function normalizeCode(code) {
  return String(code || "").trim().toUpperCase();
}

async function ensureDataFiles() {
  await fs.mkdir(DATA_DIR, { recursive: true });
  await ensureJsonFile(SESSIONS_FILE, []);
  await ensureJsonFile(SUBMISSIONS_FILE, []);
}

async function ensureJsonFile(filePath, defaultValue) {
  try {
    await fs.access(filePath);
  } catch {
    await fs.writeFile(filePath, JSON.stringify(defaultValue, null, 2));
  }
}

async function readJson(filePath, fallback) {
  try {
    const raw = await fs.readFile(filePath, "utf8");
    return JSON.parse(raw || "null") ?? fallback;
  } catch (error) {
    if (error.code === "ENOENT") return fallback;
    throw error;
  }
}

async function writeJson(filePath, value) {
  await fs.writeFile(filePath, `${JSON.stringify(value, null, 2)}\n`);
}

async function parseBody(req) {
  return new Promise((resolve, reject) => {
    let raw = "";
    req.on("data", (chunk) => {
      raw += chunk;
      if (raw.length > 1_000_000) {
        reject(Object.assign(new Error("Request body too large"), { status: 413 }));
        req.destroy();
      }
    });
    req.on("end", () => {
      if (!raw) {
        resolve({});
        return;
      }
      try {
        resolve(JSON.parse(raw));
      } catch {
        reject(Object.assign(new Error("Invalid JSON body"), { status: 400 }));
      }
    });
    req.on("error", reject);
  });
}

function sendJson(res, status, payload) {
  res.writeHead(status, {
    "Content-Type": "application/json; charset=utf-8",
    "Cache-Control": "no-store",
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET,POST,OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type"
  });
  res.end(JSON.stringify(payload, null, 2));
}

function sendError(res, status, message, details) {
  sendJson(res, status, { error: { message, details } });
}

async function activateMedicalHistory(req, res) {
  const body = await parseBody(req);
  if (!isValidCode(body.code)) {
    sendError(res, 422, "Activation code must be exactly 6 alphanumeric characters.");
    return;
  }

  const code = normalizeCode(body.code);
  const now = new Date();
  const expiresAt = new Date(now.getTime() + 2 * 60 * 60 * 1000);
  const sessions = await readJson(SESSIONS_FILE, []);
  const existingIndex = sessions.findIndex((session) => session.code === code && session.status !== "expired");
  const activation = {
    activationId: crypto.randomUUID(),
    code,
    status: "active",
    receivedAt: now.toISOString(),
    expiresAt: expiresAt.toISOString(),
    context: {
      patientId: body.patientId || null,
      encounterId: body.encounterId || null,
      requestedByModule: body.requestedByModule || null,
      returnUrl: body.returnUrl || null
    }
  };

  if (existingIndex >= 0) {
    sessions[existingIndex] = activation;
  } else {
    sessions.push(activation);
  }

  await writeJson(SESSIONS_FILE, sessions);
  sendJson(res, 201, {
    ...activation,
    launchUrl: `/?code=${encodeURIComponent(code)}`
  });
}

async function getActivation(req, res, code) {
  if (!isValidCode(code)) {
    sendError(res, 422, "Activation code must be exactly 6 alphanumeric characters.");
    return;
  }

  const normalizedCode = normalizeCode(code);
  const sessions = await readJson(SESSIONS_FILE, []);
  const activation = sessions.find((session) => session.code === normalizedCode);

  if (!activation) {
    sendError(res, 404, "No active Medical History session found for this code.");
    return;
  }

  if (new Date(activation.expiresAt).getTime() < Date.now()) {
    activation.status = "expired";
    await writeJson(SESSIONS_FILE, sessions);
    sendError(res, 410, "This Medical History activation code has expired.");
    return;
  }

  sendJson(res, 200, activation);
}

function validateSubmission(body) {
  const errors = [];
  if (!isValidCode(body.code)) errors.push("code must be exactly 6 alphanumeric characters");
  if (!Array.isArray(body.pastMedicalHistory)) errors.push("pastMedicalHistory must be an array");
  if (!Array.isArray(body.drugs)) errors.push("drugs must be an array");
  const history = Array.isArray(body.pastMedicalHistory) ? body.pastMedicalHistory : [];
  if (history.some((condition) => !COMORBIDITY_OPTIONS.includes(condition))) errors.push("pastMedicalHistory contains an unsupported condition");
  const drugs = Array.isArray(body.drugs) ? body.drugs : [];
  if (drugs.length > 20) errors.push("drugs cannot contain more than 20 entries");
  drugs.forEach((drug, index) => {
    if (!drug || typeof drug.name !== "string" || drug.name.trim().length === 0) errors.push(`drugs[${index}].name is required`);
  });
  ["substantialSuicideRisk", "priorAntipsychoticTherapy", "clozapineContraindication", "recurrentNonAdherenceDeterioration"].forEach((field) => {
    if (typeof body[field] !== "boolean") errors.push(`${field} must be a boolean`);
  });
  if (body.priorAntipsychoticTherapy === true) {
    if (typeof body.priorAntipsychoticTherapySuccessful !== "boolean") errors.push("priorAntipsychoticTherapySuccessful must be a boolean when priorAntipsychoticTherapy is true");
    if (!ANTIPSYCHOTIC_OPTIONS.includes(body.antipsychotic)) errors.push("antipsychotic must be selected from the supported options when priorAntipsychoticTherapy is true");
  }
  const contraindications = body.clozapineContraindications;
  if (!Array.isArray(contraindications)) errors.push("clozapineContraindications must be an array");
  if (Array.isArray(contraindications)) {
    if (contraindications.some((item) => !CLOZAPINE_CONTRAINDICATION_OPTIONS.includes(item))) errors.push("clozapineContraindications contains an unsupported option");
    if (body.clozapineContraindication === true && contraindications.length === 0) errors.push("at least one clozapine contraindication is required when clozapineContraindication is true");
    if (body.clozapineContraindication === false && contraindications.length > 0) errors.push("clozapineContraindications must be empty when clozapineContraindication is false");
  }
  return errors;
}
async function submitMedicalHistory(req, res) {
  const body = await parseBody(req);
  const errors = validateSubmission(body);
  if (errors.length) {
    sendError(res, 422, "Medical History submission failed validation.", errors);
    return;
  }

  const code = normalizeCode(body.code);
  const sessions = await readJson(SESSIONS_FILE, []);
  const activation = sessions.find((session) => session.code === code);
  if (!activation || activation.status === "expired") {
    sendError(res, 404, "Submit requires an active Medical History activation code.");
    return;
  }

  const submissions = await readJson(SUBMISSIONS_FILE, []);
  const submission = {
    submissionId: crypto.randomUUID(),
    code,
    patientId: activation.context.patientId,
    encounterId: activation.context.encounterId,
    pastMedicalHistory: body.pastMedicalHistory.map(String),
    drugs: body.drugs.map((drug) => ({
      name: String(drug.name).trim(),
      dose: drug.dose ? String(drug.dose).trim() : "",
      route: drug.route ? String(drug.route).trim() : "",
      frequency: drug.frequency ? String(drug.frequency).trim() : ""
    })),
    substantialSuicideRisk: body.substantialSuicideRisk,
    priorAntipsychoticTherapy: body.priorAntipsychoticTherapy,
    priorAntipsychoticTherapySuccessful: body.priorAntipsychoticTherapy ? body.priorAntipsychoticTherapySuccessful : null,
    antipsychotic: body.priorAntipsychoticTherapy ? body.antipsychotic : null,
    clozapineContraindication: body.clozapineContraindication,
    clozapineContraindications: body.clozapineContraindication ? body.clozapineContraindications.map(String) : [],
    recurrentNonAdherenceDeterioration: body.recurrentNonAdherenceDeterioration,
    submittedAt: new Date().toISOString(),
    submittedBy: body.submittedBy || "standalone-ui",
    source: body.source || "medical-history-module"
  };

  submissions.push(submission);
  activation.status = "submitted";
  activation.submissionId = submission.submissionId;
  activation.submittedAt = submission.submittedAt;

  await writeJson(SUBMISSIONS_FILE, submissions);
  await writeJson(SESSIONS_FILE, sessions);
  sendJson(res, 201, submission);
}

async function listSubmissions(req, res, url) {
  const submissions = await readJson(SUBMISSIONS_FILE, []);
  const code = url.searchParams.get("code");
  if (code) {
    sendJson(res, 200, submissions.filter((submission) => submission.code === normalizeCode(code)));
    return;
  }
  sendJson(res, 200, submissions);
}

async function serveStatic(req, res, url) {
  const requestedPath = url.pathname === "/" ? "/index.html" : decodeURIComponent(url.pathname);
  const filePath = path.normalize(path.join(PUBLIC_DIR, requestedPath));

  if (!filePath.startsWith(PUBLIC_DIR)) {
    sendError(res, 403, "Forbidden path.");
    return;
  }

  try {
    const body = await fs.readFile(filePath);
    const contentType = MIME_TYPES[path.extname(filePath)] || "application/octet-stream";
    res.writeHead(200, { "Content-Type": contentType });
    res.end(body);
  } catch (error) {
    if (error.code === "ENOENT") {
      res.writeHead(302, { Location: "/" });
      res.end();
      return;
    }
    throw error;
  }
}

async function route(req, res) {
  const url = new URL(req.url, `http://${req.headers.host}`);

  if (req.method === "OPTIONS") {
    sendJson(res, 204, {});
    return;
  }

  if (req.method === "GET" && url.pathname === "/api/internal/medical-history/health") {
    sendJson(res, 200, { status: "ok", module: "Medical History" });
    return;
  }

  if (req.method === "GET" && url.pathname === "/api/internal/medical-history/options") {
    sendJson(res, 200, { pastMedicalHistory: COMORBIDITY_OPTIONS, antipsychotics: ANTIPSYCHOTIC_OPTIONS, clozapineContraindications: CLOZAPINE_CONTRAINDICATION_OPTIONS });
    return;
  }

  if (req.method === "GET" && url.pathname === "/api/internal/medical-history/schema") {
    sendJson(res, 200, await readJson(SCHEMA_FILE, {}));
    return;
  }

  if (req.method === "POST" && url.pathname === "/api/internal/medical-history/activate") {
    await activateMedicalHistory(req, res);
    return;
  }

  const activationMatch = url.pathname.match(/^\/api\/internal\/medical-history\/activation\/([A-Za-z0-9]{1,20})$/);
  if (req.method === "GET" && activationMatch) {
    await getActivation(req, res, activationMatch[1]);
    return;
  }

  if (req.method === "POST" && url.pathname === "/api/internal/medical-history/submissions") {
    await submitMedicalHistory(req, res);
    return;
  }

  if (req.method === "GET" && url.pathname === "/api/internal/medical-history/submissions") {
    await listSubmissions(req, res, url);
    return;
  }

  if (req.method === "GET") {
    await serveStatic(req, res, url);
    return;
  }

  sendError(res, 405, "Method not allowed.");
}

ensureDataFiles()
  .then(() => {
    http
      .createServer((req, res) => {
        route(req, res).catch((error) => {
          const status = error.status || 500;
          sendError(res, status, error.message || "Internal server error");
        });
      })
      .listen(PORT, () => {
        console.log(`Medical History module running at http://localhost:${PORT}`);
      });
  })
  .catch((error) => {
    console.error("Failed to start Medical History module:", error);
    process.exit(1);
  });


