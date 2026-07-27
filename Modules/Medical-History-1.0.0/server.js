const http = require("http");
const fs = require("fs/promises");
const path = require("path");
const crypto = require("crypto");
const {
  MedicalHistorySubmissionStore,
  isCanonicalUuid,
  structureCondition,
  structureMedication,
} = require("./medical-history-submission.js");
const {
  createDefaultMedicalHistoryRepository,
} = require("./repository.js");
const { createHttpAuthAdapter } = require("./auth-adapter.js");
const { createSecurity } = require("./security.js");
const { createReadinessProbe } = require("./readiness.js");

const PORT = Number(process.env.PORT || 4173);
const ROOT_DIR = __dirname;
const PUBLIC_DIR = path.join(ROOT_DIR, "public");
const SCHEMA_FILE = path.join(ROOT_DIR, "data", "medical_history_schema.json");

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

function corsOrigins() {
  const raw = process.env.MEDICAL_HISTORY_CORS_ORIGINS;
  if (raw && raw.trim()) {
    return raw.split(",").map((part) => part.trim()).filter(Boolean);
  }
  if (process.env.NODE_ENV === "production") return [];
  return ["*"];
}

function applyCors(res, req) {
  const origins = corsOrigins();
  const requestOrigin = req.headers.origin;
  if (origins.includes("*")) {
    res.setHeader("Access-Control-Allow-Origin", "*");
  } else if (requestOrigin && origins.includes(requestOrigin)) {
    res.setHeader("Access-Control-Allow-Origin", requestOrigin);
    res.setHeader("Vary", "Origin");
  }
  res.setHeader("Access-Control-Allow-Methods", "GET,POST,OPTIONS");
  res.setHeader("Access-Control-Allow-Headers", "Content-Type, X-CSRF-Token");
  if (process.env.MEDICAL_HISTORY_CORS_CREDENTIALS === "1") {
    res.setHeader("Access-Control-Allow-Credentials", "true");
  }
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

function sendJson(res, req, status, payload, headers = {}) {
  applyCors(res, req);
  res.writeHead(status, {
    "Content-Type": "application/json; charset=utf-8",
    "Cache-Control": "no-store",
    ...headers,
  });
  res.end(JSON.stringify(payload, null, 2));
}

function sendError(res, req, status, message, details) {
  sendJson(res, req, status, { error: { message, details } });
}

function validateSubmission(body, { requireCode = true } = {}) {
  const errors = [];
  if (requireCode && !isValidCode(body.code)) errors.push("code must be exactly 6 alphanumeric characters");
  if (!Array.isArray(body.pastMedicalHistory)) errors.push("pastMedicalHistory must be an array");
  if (!Array.isArray(body.drugs)) errors.push("drugs must be an array");
  const history = Array.isArray(body.pastMedicalHistory) ? body.pastMedicalHistory : [];
  const historyTexts = history.map((condition) => (
    typeof condition === "string"
      ? condition
      : condition && typeof condition === "object"
        ? String(condition.originalText ?? condition.text ?? condition.name ?? "")
        : ""
  ));
  if (historyTexts.some((condition) => !COMORBIDITY_OPTIONS.includes(condition))) {
    errors.push("pastMedicalHistory contains an unsupported condition");
  }
  const drugs = Array.isArray(body.drugs) ? body.drugs : [];
  if (drugs.length > 20) errors.push("drugs cannot contain more than 20 entries");
  drugs.forEach((drug, index) => {
    const originalText = drug && typeof drug === "object"
      ? String(drug.originalText ?? drug.name ?? "").trim()
      : "";
    if (!originalText) errors.push(`drugs[${index}].name is required`);
    if (drug && drug.doseAmount !== undefined && drug.doseAmount !== null && drug.doseAmount !== "" && !Number.isFinite(Number(drug.doseAmount))) {
      errors.push(`drugs[${index}].doseAmount must be a finite number when provided`);
    }
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

function submissionData(body) {
  return {
    pastMedicalHistory: body.pastMedicalHistory.map(structureCondition),
    drugs: body.drugs.map(structureMedication),
    substantialSuicideRisk: body.substantialSuicideRisk,
    priorAntipsychoticTherapy: body.priorAntipsychoticTherapy,
    priorAntipsychoticTherapySuccessful: body.priorAntipsychoticTherapy ? body.priorAntipsychoticTherapySuccessful : null,
    antipsychotic: body.priorAntipsychoticTherapy ? body.antipsychotic : null,
    clozapineContraindication: body.clozapineContraindication,
    clozapineContraindications: body.clozapineContraindication ? body.clozapineContraindications.map(String) : [],
    recurrentNonAdherenceDeterioration: body.recurrentNonAdherenceDeterioration,
  };
}

function legacySubmissionResponse(submission) {
  return {
    ...submission,
    patientId: submission.legacyPatientId ?? submission.patientId,
    encounterId: submission.legacyEncounterId ?? submission.encounterId,
    submittedBy: submission.author,
  };
}

function identityFromUrl(url) {
  const patientId = url.searchParams.get("patientId");
  const encounterId = url.searchParams.get("encounterId");
  if (!isCanonicalUuid(patientId) || !isCanonicalUuid(encounterId)) {
    const error = new Error("patientId and encounterId must be canonical non-nil UUIDs");
    error.status = 422;
    throw error;
  }
  return { patientId, encounterId };
}

function createServer(options = {}) {
  const repository = options.repository || createDefaultMedicalHistoryRepository({
    dataDir: options.dataDir || process.env.MEDICAL_HISTORY_DATA_DIR || path.join(ROOT_DIR, "data"),
  });
  const submissionStore = options.submissionStore || new MedicalHistorySubmissionStore({ repository });
  const configuredAuthAdapter = options.authAdapter === undefined
    ? (process.env.AUTH_SESSION_URL ? createHttpAuthAdapter() : null)
    : options.authAdapter;
  const security = options.security || createSecurity({
    authAdapter: configuredAuthAdapter,
    csrfSecret: options.csrfSecret,
  });
  const readiness = options.readiness || createReadinessProbe({
    repository,
    authConfigured: security.authConfigured,
    csrfConfigured: security.csrfConfigured,
  });

  async function sendSubmission(req, res, submission, status = 200) {
    if (!submission) {
      sendError(res, req, 404, "Medical History submission was not found.");
      return;
    }
    sendJson(res, req, status, submission, { ETag: submission.etag });
  }

  async function activateMedicalHistory(req, res) {
    const body = await parseBody(req);
    if (!isValidCode(body.code)) {
      sendError(res, req, 422, "Activation code must be exactly 6 alphanumeric characters.");
      return;
    }

    const code = normalizeCode(body.code);
    const now = new Date();
    const expiresAt = new Date(now.getTime() + 2 * 60 * 60 * 1000);
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

    await repository.upsertActivation(activation);
    if (typeof repository.appendAudit === "function") {
      repository.appendAudit({
        action: "activation.upsert",
        actor: req.auth?.userId || "anonymous",
        role: req.auth?.roles?.[0] || null,
        detail: { code },
      });
    }
    sendJson(res, req, 201, {
      ...activation,
      launchUrl: `/modules/medical-history?code=${encodeURIComponent(code)}`
    });
  }

  async function getActivation(req, res, code) {
    if (!isValidCode(code)) {
      sendError(res, req, 422, "Activation code must be exactly 6 alphanumeric characters.");
      return;
    }

    const normalizedCode = normalizeCode(code);
    const activation = repository.getActivationByCode(normalizedCode);

    if (!activation) {
      sendError(res, req, 404, "No active Medical History session found for this code.");
      return;
    }

    if (new Date(activation.expiresAt).getTime() < Date.now()) {
      activation.status = "expired";
      await repository.replaceActivation(activation);
      sendError(res, req, 410, "This Medical History activation code has expired.");
      return;
    }

    sendJson(res, req, 200, activation);
  }

  async function submitMedicalHistory(req, res) {
    const body = await parseBody(req);
    const legacy = Object.prototype.hasOwnProperty.call(body, "code");
    const errors = validateSubmission(body, { requireCode: legacy });
    if (!legacy && !isCanonicalUuid(body.patientId)) errors.push("patientId must be a canonical non-nil UUID");
    if (!legacy && !isCanonicalUuid(body.encounterId)) errors.push("encounterId must be a canonical non-nil UUID");
    if (errors.length) {
      sendError(res, req, 422, "Medical History submission failed validation.", errors);
      return;
    }

    const data = submissionData(body);
    let submission;
    if (legacy) {
      const code = normalizeCode(body.code);
      const activation = repository.getActivationByCode(code);
      if (!activation || activation.status === "expired") {
        sendError(res, req, 404, "Submit requires an active Medical History activation code.");
        return;
      }
      const patientId = isCanonicalUuid(activation.context.patientId) ? activation.context.patientId : null;
      const encounterId = isCanonicalUuid(activation.context.encounterId) ? activation.context.encounterId : null;
      const resource = submissionStore.buildResource({
        patientId,
        encounterId,
        legacyPatientId: activation.context.patientId,
        legacyEncounterId: activation.context.encounterId,
        author: body.submittedBy || "standalone-ui",
        data,
        code,
        source: body.source || "medical-history-module",
        allowLegacyIdentity: true,
      });
      activation.status = "submitted";
      activation.submissionId = resource.submissionId;
      activation.submittedAt = resource.submittedAt;
      const result = await repository.submitLegacyWithActivation({
        activation,
        submission: resource,
      });
      submission = result.submission;
      if (typeof repository.appendAudit === "function") {
        repository.appendAudit({
          action: "submission.create",
          actor: req.auth?.userId || resource.author,
          role: req.auth?.roles?.[0] || null,
          patientId: resource.patientId,
          submissionId: resource.submissionId,
          detail: { mode: "legacy", code },
        });
      }
      await sendSubmission(req, res, legacySubmissionResponse(submission), 201);
      return;
    }

    submission = await submissionStore.create({
      patientId: body.patientId,
      encounterId: body.encounterId,
      author: body.author || body.submittedBy,
      data,
      status: body.status || "submitted",
      source: body.source || "medical-history-module",
    });
    if (typeof repository.appendAudit === "function") {
      repository.appendAudit({
        action: "submission.create",
        actor: req.auth?.userId || submission.author,
        role: req.auth?.roles?.[0] || null,
        patientId: submission.patientId,
        submissionId: submission.submissionId,
        detail: { mode: "canonical" },
      });
    }
    await sendSubmission(req, res, submission, 201);
  }

  async function listSubmissions(req, res, url) {
    const code = url.searchParams.get("code");
    const submissions = repository.listSubmissions(code ? { code: normalizeCode(code) } : {});
    sendJson(res, req, 200, submissions);
  }

  async function getLatestSubmission(req, res, url) {
    const submission = await submissionStore.getLatest(identityFromUrl(url));
    await sendSubmission(req, res, submission);
  }

  async function getSubmissionHistory(req, res, url) {
    const history = await submissionStore.getHistory(identityFromUrl(url));
    sendJson(res, req, 200, history, history.length ? { ETag: history[history.length - 1].etag } : {});
  }

  async function getSubmission(req, res, id) {
    await sendSubmission(req, res, await submissionStore.findById(id));
  }

  async function serveStatic(req, res, url) {
    const requestedPath = url.pathname === "/" ? "/index.html" : decodeURIComponent(url.pathname);
    const filePath = path.normalize(path.join(PUBLIC_DIR, requestedPath));

    if (!filePath.startsWith(PUBLIC_DIR)) {
      sendError(res, req, 403, "Forbidden path.");
      return;
    }

    try {
      const body = await fs.readFile(filePath);
      const contentType = MIME_TYPES[path.extname(filePath)] || "application/octet-stream";
      applyCors(res, req);
      res.writeHead(200, { "Content-Type": contentType });
      res.end(body);
    } catch (error) {
      if (error.code === "ENOENT") {
        sendError(res, req, 404, "Static file was not found.");
        return;
      }
      throw error;
    }
  }

  async function authorize(req, res, roles, { csrf = false } = {}) {
    if (!security) return true;
    if (roles && roles.length) {
      const ok = await security.enforceRole(req, res, roles);
      if (!ok) return false;
    }
    if (csrf) {
      const ok = security.enforceCsrf(req, res);
      if (!ok) return false;
    }
    return true;
  }

  async function route(req, res) {
    const url = new URL(req.url, `http://${req.headers.host}`);

    if (req.method === "OPTIONS") {
      sendJson(res, req, 204, {});
      return;
    }

    if (req.method === "GET" && url.pathname === "/api/internal/medical-history/health") {
      sendJson(res, req, 200, { status: "ok", module: "Medical History" });
      return;
    }

    if (req.method === "GET" && (url.pathname === "/ready" || url.pathname === "/api/internal/medical-history/ready")) {
      const result = typeof readiness === "function" ? readiness() : readiness;
      sendJson(res, req, result.ok ? 200 : 503, result);
      return;
    }

    if (req.method === "GET" && url.pathname === "/api/internal/medical-history/csrf") {
      if (!(await authorize(req, res, ["psychiatrist", "admin"]))) return;
      if (!security) {
        sendError(res, req, 503, "CSRF is not configured.");
        return;
      }
      security.issueToken(req, res);
      return;
    }

    if (req.method === "GET" && url.pathname === "/api/internal/medical-history/options") {
      sendJson(res, req, 200, { pastMedicalHistory: COMORBIDITY_OPTIONS, antipsychotics: ANTIPSYCHOTIC_OPTIONS, clozapineContraindications: CLOZAPINE_CONTRAINDICATION_OPTIONS });
      return;
    }

    if (req.method === "GET" && url.pathname === "/api/internal/medical-history/schema") {
      sendJson(res, req, 200, JSON.parse(await fs.readFile(SCHEMA_FILE, "utf8")));
      return;
    }

    if (req.method === "POST" && url.pathname === "/api/internal/medical-history/activate") {
      if (!(await authorize(req, res, ["psychiatrist", "admin"], { csrf: true }))) return;
      await activateMedicalHistory(req, res);
      return;
    }

    const activationMatch = url.pathname.match(/^\/api\/internal\/medical-history\/activation\/([A-Za-z0-9]{1,20})$/);
    if (req.method === "GET" && activationMatch) {
      if (!(await authorize(req, res, ["psychiatrist", "admin", "nurse"]))) return;
      await getActivation(req, res, activationMatch[1]);
      return;
    }

    if (req.method === "POST" && url.pathname === "/api/internal/medical-history/submissions") {
      if (!(await authorize(req, res, ["psychiatrist"], { csrf: true }))) return;
      await submitMedicalHistory(req, res);
      return;
    }

    if (req.method === "GET" && url.pathname === "/api/internal/medical-history/submissions") {
      if (!(await authorize(req, res, ["psychiatrist", "admin"]))) return;
      await listSubmissions(req, res, url);
      return;
    }

    if (req.method === "GET" && url.pathname === "/api/internal/medical-history/submissions/latest") {
      if (!(await authorize(req, res, ["psychiatrist", "admin"]))) return;
      await getLatestSubmission(req, res, url);
      return;
    }

    if (req.method === "GET" && url.pathname === "/api/internal/medical-history/submissions/history") {
      if (!(await authorize(req, res, ["psychiatrist", "admin"]))) return;
      await getSubmissionHistory(req, res, url);
      return;
    }

    const submissionMatch = url.pathname.match(/^\/api\/internal\/medical-history\/submissions\/([^/]+)$/);
    if (req.method === "GET" && submissionMatch) {
      if (!(await authorize(req, res, ["psychiatrist", "admin"]))) return;
      await getSubmission(req, res, submissionMatch[1]);
      return;
    }

    if (req.method === "GET") {
      await serveStatic(req, res, url);
      return;
    }

    sendError(res, req, 405, "Method not allowed.");
  }

  const server = http.createServer((req, res) => {
    route(req, res).catch((error) => {
      const status = error.status || 500;
      sendError(res, req, status, error.message || "Internal server error");
    });
  });

  server.repository = repository;
  server.submissionStore = submissionStore;
  return server;
}

function start(port = PORT) {
  const server = createServer();
  server.listen(port, () => {
    console.log(`Medical History module running at http://localhost:${port}`);
  });
  return server;
}

if (require.main === module) {
  start();
}

module.exports = {
  createServer,
  start,
  corsOrigins,
};
