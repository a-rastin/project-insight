const crypto = require("node:crypto");
const fs = require("node:fs");
const fsp = require("node:fs/promises");
const http = require("node:http");
const path = require("node:path");

const PORT = Number(process.env.PORT || 8111);
const ROOT = __dirname;
const PUBLIC_FILES = new Map([
  ["/", "index.html"],
  ["/index.html", "index.html"],
  ["/app.js", "app.js"],
  ["/styles.css", "styles.css"],
]);
const UUID = /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;
const CODE = /^[A-Za-z0-9]{6}$/;
const ANSWER_KEYS = ["q1", "q2", "q3", "q4", "q5", "q6", "q6Recent"];

function clone(value) {
  return JSON.parse(JSON.stringify(value));
}

function normalizeCode(code) {
  return String(code || "").trim().toUpperCase();
}

function validUuid(value) {
  return typeof value === "string" && UUID.test(value) && value !== "00000000-0000-0000-0000-000000000000";
}

function createHttpAuthAdapter({ sessionUrl = process.env.AUTH_SESSION_URL, fetchImpl = globalThis.fetch } = {}) {
  if (!sessionUrl) throw new Error("AUTH_SESSION_URL is required");
  const origin = new URL(sessionUrl).origin;
  return {
    async verify(cookie) {
      if (!cookie) return null;
      const response = await fetchImpl(sessionUrl, { headers: { accept: "application/json", cookie } });
      if (!response.ok || new URL(sessionUrl).origin !== origin) return null;
      const payload = await response.json();
      if (payload?.schemaVersion !== "1.0.0" || payload.authenticated !== true || payload.gates?.disclaimerAccepted !== true || payload.gates?.passwordChangeRequired !== false) return null;
      if (!payload.user?.id || !Array.isArray(payload.user.roles) || payload.user.roles.some((role) => typeof role !== "string" || role !== role.toLowerCase())) return null;
      if (!Number.isFinite(Date.parse(payload.session?.expiresAt || "")) || Date.parse(payload.session.expiresAt) <= Date.now()) return null;
      return { userId: payload.user.id, roles: payload.user.roles };
    },
  };
}

function createRepository(state = { activations: {}, assessments: {} }, persist = async () => {}) {
  return {
    ping() {
      return true;
    },
    getActivation(code) {
      return state.activations[normalizeCode(code)] ? clone(state.activations[normalizeCode(code)]) : null;
    },
    getAssessment(code) {
      return state.assessments[normalizeCode(code)] ? clone(state.assessments[normalizeCode(code)]) : null;
    },
    async saveActivation(activation) {
      state.activations[activation.code] = clone(activation);
      await persist();
      return clone(activation);
    },
    async saveAssessment(assessment) {
      state.assessments[assessment.code] = clone(assessment);
      await persist();
      return clone(assessment);
    },
  };
}

function createMemoryRepository(seed) {
  return createRepository(clone(seed || { activations: {}, assessments: {} }));
}

function createFileRepository(dataDir = process.env.SUICIDE_RISK_DATA_DIR || path.join(ROOT, "data")) {
  fs.mkdirSync(dataDir, { recursive: true });
  const file = path.join(dataDir, "suicide_risk.json");
  let state = { activations: {}, assessments: {} };
  if (fs.existsSync(file)) {
    const parsed = JSON.parse(fs.readFileSync(file, "utf8"));
    if (parsed && typeof parsed === "object" && parsed.activations && parsed.assessments) state = parsed;
  }
  let writes = Promise.resolve();
  const persist = () => {
    writes = writes.then(async () => {
      const temporary = `${file}.${process.pid}.tmp`;
      await fsp.writeFile(temporary, JSON.stringify(state, null, 2));
      await fsp.rename(temporary, file);
    });
    return writes;
  };
  return createRepository(state, persist);
}

function json(res, status, body, headers = {}) {
  res.writeHead(status, { "Content-Type": "application/json; charset=utf-8", "Cache-Control": "no-store", ...headers });
  res.end(JSON.stringify(body));
}

function error(res, status, message) {
  json(res, status, { error: { message } });
}

function readBody(req) {
  return new Promise((resolve, reject) => {
    let raw = "";
    req.on("data", (chunk) => {
      raw += chunk;
      if (raw.length > 1_000_000) req.destroy(Object.assign(new Error("Request body too large"), { status: 413 }));
    });
    req.on("end", () => {
      try {
        resolve(raw ? JSON.parse(raw) : {});
      } catch {
        reject(Object.assign(new Error("Invalid JSON body"), { status: 400 }));
      }
    });
    req.on("error", reject);
  });
}

function createSecurity({ authAdapter = null, csrfSecret = process.env.SUICIDE_RISK_CSRF_SECRET || crypto.randomBytes(32) } = {}) {
  const secret = Buffer.from(String(csrfSecret));
  const sign = (raw) => `${raw}.${crypto.createHmac("sha256", secret).update(raw).digest("hex")}`;
  const valid = (token) => {
    if (typeof token !== "string" || !token.includes(".")) return false;
    const [raw, signature] = token.split(".");
    const expected = crypto.createHmac("sha256", secret).update(raw).digest("hex");
    return signature.length === expected.length && crypto.timingSafeEqual(Buffer.from(signature), Buffer.from(expected));
  };
  return {
    configured: Boolean(authAdapter),
    async authorize(req, res) {
      if (!authAdapter) return true;
      const session = await authAdapter.verify(req.headers.cookie);
      if (!session) {
        error(res, 401, "Authentication required");
        return false;
      }
      if (!session.roles?.includes("psychiatrist")) {
        error(res, 403, "Forbidden");
        return false;
      }
      req.auth = session;
      return true;
    },
    issue(req, res) {
      const token = sign(crypto.randomBytes(16).toString("hex"));
      res.setHeader("Set-Cookie", `csrf=${token}; Path=/; SameSite=Lax${process.env.SUICIDE_RISK_CSRF_SECURE === "1" ? "; Secure" : ""}`);
      json(res, 200, { token });
    },
    csrf(req, res) {
      if (!authAdapter) return true;
      const token = String(req.headers.cookie || "").split(";").map((entry) => entry.trim()).find((entry) => entry.startsWith("csrf="))?.slice(5);
      if (!token || token !== req.headers["x-csrf-token"] || !valid(token)) {
        error(res, 403, "CSRF token missing or invalid");
        return false;
      }
      return true;
    },
  };
}

function evaluateAnswers(answers) {
  const required = ["q1", "q2", "q6"];
  if (answers.q2 === true) required.push("q3", "q4", "q5");
  if (answers.q6 === true) required.push("q6Recent");
  if (required.some((key) => answers[key] === null)) throw new Error("All required C-SSRS answers must be completed");
  let score = 0;
  for (const [key, value] of Object.entries(answers)) {
    if (value === true && /^q[1-5]$/.test(key)) score = Math.max(score, Number(key.slice(1)));
  }
  if (answers.q6Recent === true) score = Math.max(score, 6);
  if (answers.q4 || answers.q5 || answers.q6Recent) return { score, result: "High risk", riskLevel: "high" };
  if (answers.q3 || answers.q6) return { score, result: "Moderate risk", riskLevel: "moderate" };
  if (answers.q1 || answers.q2) return { score, result: "Low risk", riskLevel: "low" };
  return { score, result: "No current risk endorsed", riskLevel: "none" };
}

function validateAssessment(body) {
  if (body.status !== "completed") throw Object.assign(new Error("Workflow assessments must be completed; unassessed bypass is not supported"), { status: 422 });
  if (!body.answers || typeof body.answers !== "object" || Array.isArray(body.answers)) throw Object.assign(new Error("answers must be an object"), { status: 422 });
  for (const key of ANSWER_KEYS) {
    if (!(key in body.answers) || ![true, false, null].includes(body.answers[key])) {
      throw Object.assign(new Error(`answers.${key} must be boolean or null`), { status: 422 });
    }
  }
  if (Object.keys(body.answers).some((key) => !ANSWER_KEYS.includes(key))) throw Object.assign(new Error("answers contains unsupported fields"), { status: 422 });
  const computed = evaluateAnswers(body.answers);
  if (body.score !== computed.score || body.result !== computed.result || body.riskLevel !== computed.riskLevel) {
    throw Object.assign(new Error("score and risk result must match C-SSRS answers"), { status: 422 });
  }
  if (!Number.isFinite(Date.parse(body.completedAt || ""))) throw Object.assign(new Error("completedAt must be an ISO timestamp"), { status: 422 });
  return computed;
}

function sameContext(existing, body) {
  return existing.context.patientId === (body.patientId || null)
    && existing.context.encounterId === (body.encounterId || null)
    && existing.context.requestedByModule === (body.requestedByModule || null)
    && existing.context.returnUrl === (body.returnUrl || null);
}

function createServer({ repository = createFileRepository(), authAdapter, csrfSecret } = {}) {
  const security = createSecurity({ authAdapter: authAdapter === undefined && process.env.AUTH_SESSION_URL ? createHttpAuthAdapter() : authAdapter, csrfSecret });

  return http.createServer(async (req, res) => {
    try {
      const url = new URL(req.url, "http://localhost");
      if (req.method === "GET" && (url.pathname === "/health" || url.pathname === "/api/suicide-risk/v1/health")) {
        json(res, 200, { ok: true, module: "suicide-risk" });
        return;
      }
      if (req.method === "GET" && (url.pathname === "/ready" || url.pathname === "/api/suicide-risk/v1/ready")) {
        json(res, repository.ping() ? 200 : 503, { ok: repository.ping(), module: "suicide-risk", checks: { persistence: repository.ping() ? "ok" : "blocked", authentication: security.configured ? "ok" : "disabled", csrf: "ok" } });
        return;
      }
      if (req.method === "GET" && url.pathname === "/api/suicide-risk/v1/csrf") {
        if (await security.authorize(req, res)) security.issue(req, res);
        return;
      }
      if (req.method === "POST" && url.pathname === "/api/suicide-risk/v1/activate") {
        if (!(await security.authorize(req, res)) || !security.csrf(req, res)) return;
        const body = await readBody(req);
        if (!CODE.test(String(body.code || "").trim())) return error(res, 422, "Activation code must be exactly 6 alphanumeric characters");
        if ((body.patientId !== undefined && !validUuid(body.patientId)) || (body.encounterId !== undefined && !validUuid(body.encounterId))) return error(res, 422, "patientId and encounterId must be canonical non-nil UUIDs when supplied");
        const code = normalizeCode(body.code);
        const existing = repository.getActivation(code);
        if (existing) {
          if (!sameContext(existing, body)) return error(res, 409, "Activation context conflicts with the existing assessment workflow");
          return json(res, 200, existing);
        }
        const activation = {
          activationId: crypto.randomUUID(), code, status: "active", receivedAt: new Date().toISOString(),
          context: { patientId: body.patientId || null, encounterId: body.encounterId || null, requestedByModule: body.requestedByModule || null, returnUrl: body.returnUrl || null },
        };
        await repository.saveActivation(activation);
        json(res, 201, activation);
        return;
      }
      const activationMatch = url.pathname.match(/^\/api\/suicide-risk\/v1\/activation\/([A-Za-z0-9]{1,20})$/);
      if (req.method === "GET" && activationMatch) {
        if (!(await security.authorize(req, res))) return;
        const activation = repository.getActivation(activationMatch[1]);
        if (!activation) return error(res, 404, "No active Suicide Risk workflow found for this code");
        json(res, 200, activation);
        return;
      }
      const assessmentMatch = url.pathname.match(/^\/api\/suicide-risk\/v1\/assessments\/([A-Za-z0-9]{1,20})$/);
      if (assessmentMatch && req.method === "GET") {
        if (!(await security.authorize(req, res))) return;
        const assessment = repository.getAssessment(assessmentMatch[1]);
        if (!assessment) return error(res, 404, "Suicide Risk assessment was not found");
        json(res, 200, assessment);
        return;
      }
      if (assessmentMatch && req.method === "PUT") {
        if (!(await security.authorize(req, res)) || !security.csrf(req, res)) return;
        const code = normalizeCode(assessmentMatch[1]);
        const activation = repository.getActivation(code);
        if (!activation) return error(res, 404, "Save requires an active Suicide Risk workflow");
        const existing = repository.getAssessment(code);
        if (existing) return json(res, 200, existing);
        const body = await readBody(req);
        const computed = validateAssessment(body);
        const assessment = {
          assessmentId: crypto.randomUUID(), code, patientId: activation.context.patientId, encounterId: activation.context.encounterId,
          requestedByModule: activation.context.requestedByModule, author: req.auth?.userId || "anonymous", status: "completed",
          answers: clone(body.answers), ...computed, completedAt: body.completedAt, sourceVersion: "v1.0.0", sourceRevision: "d5f462f2cabea14b042da056bdd5bbe9eb5ee1c8",
        };
        await repository.saveAssessment(assessment);
        activation.status = "completed";
        activation.assessmentId = assessment.assessmentId;
        activation.completedAt = assessment.completedAt;
        await repository.saveActivation(activation);
        json(res, 201, assessment);
        return;
      }
      if (req.method === "GET" && PUBLIC_FILES.has(url.pathname)) {
        const file = path.join(ROOT, PUBLIC_FILES.get(url.pathname));
        const contentType = file.endsWith(".css") ? "text/css; charset=utf-8" : file.endsWith(".js") ? "application/javascript; charset=utf-8" : "text/html; charset=utf-8";
        res.writeHead(200, { "Content-Type": contentType, "Cache-Control": "no-store" });
        res.end(await fsp.readFile(file));
        return;
      }
      error(res, 404, "Not found");
    } catch (caught) {
      error(res, caught.status || 500, caught.message || "Internal server error");
    }
  });
}

if (require.main === module) createServer().listen(PORT);

module.exports = { createFileRepository, createHttpAuthAdapter, createMemoryRepository, createServer, evaluateAnswers };
