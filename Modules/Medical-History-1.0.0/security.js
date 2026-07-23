const { createHmac, randomBytes, timingSafeEqual } = require("node:crypto");

function asSecret(value) {
  return Buffer.isBuffer(value) ? value : Buffer.from(String(value));
}

function applyCorsHeaders(res, req) {
  const raw = process.env.MEDICAL_HISTORY_CORS_ORIGINS;
  const origins = raw && raw.trim()
    ? raw.split(",").map((part) => part.trim()).filter(Boolean)
    : (process.env.NODE_ENV === "production" ? [] : ["*"]);
  const requestOrigin = req.headers.origin;
  if (origins.includes("*")) {
    res.setHeader("Access-Control-Allow-Origin", "*");
  } else if (requestOrigin && origins.includes(requestOrigin)) {
    res.setHeader("Access-Control-Allow-Origin", requestOrigin);
    res.setHeader("Vary", "Origin");
  }
}

function jsonError(res, req, status, message) {
  applyCorsHeaders(res, req);
  res.writeHead(status, {
    "Content-Type": "application/json; charset=utf-8",
    "Cache-Control": "no-store",
  });
  res.end(JSON.stringify({ error: { message } }, null, 2));
  return false;
}

function createSecurity({
  authAdapter = null,
  csrfSecret = process.env.MEDICAL_HISTORY_CSRF_SECRET || randomBytes(32),
} = {}) {
  const secret = asSecret(csrfSecret);

  function sign(raw) {
    return `${raw}.${createHmac("sha256", secret).update(raw).digest("hex")}`;
  }

  function mint() {
    return sign(randomBytes(16).toString("hex"));
  }

  function validToken(token) {
    if (typeof token !== "string") return false;
    const separator = token.lastIndexOf(".");
    if (separator < 1) return false;
    const raw = token.slice(0, separator);
    const signature = token.slice(separator + 1);
    const expected = createHmac("sha256", secret).update(raw).digest("hex");
    try {
      return signature.length === expected.length
        && timingSafeEqual(Buffer.from(signature), Buffer.from(expected));
    } catch {
      return false;
    }
  }

  async function enforceRole(req, res, allowedRoles) {
    if (!authAdapter) return true;
    try {
      const session = await authAdapter.verify(req.headers.cookie);
      if (!session) return jsonError(res, req, 401, "Authentication required");
      if (!allowedRoles.some((role) => session.roles.includes(role))) {
        return jsonError(res, req, 403, "Forbidden");
      }
      req.auth = session;
      return true;
    } catch {
      return jsonError(res, req, 503, "Authentication service unavailable");
    }
  }

  function issueToken(req, res) {
    const token = mint();
    const secure = process.env.MEDICAL_HISTORY_CSRF_SECURE === "1" ? "; Secure" : "";
    applyCorsHeaders(res, req);
    res.setHeader("Set-Cookie", `csrf=${token}; Path=/; SameSite=Lax${secure}`);
    res.writeHead(200, {
      "Content-Type": "application/json; charset=utf-8",
      "Cache-Control": "no-store",
    });
    res.end(JSON.stringify({ token }, null, 2));
  }

  function enforceCsrf(req, res) {
    if (!authAdapter) return true;
    const cookie = String(req.headers.cookie || "")
      .split(";")
      .map((part) => part.trim())
      .find((part) => part.startsWith("csrf="))
      ?.slice("csrf=".length);
    const header = req.headers["x-csrf-token"];
    if (!cookie || !header || cookie !== header || !validToken(cookie)) {
      return jsonError(res, req, 403, "CSRF token missing or invalid");
    }
    return true;
  }

  return {
    authConfigured: Boolean(authAdapter),
    csrfConfigured: true,
    enforceRole,
    enforceCsrf,
    issueToken,
    verifyCsrf: validToken,
  };
}

module.exports = { createSecurity };
