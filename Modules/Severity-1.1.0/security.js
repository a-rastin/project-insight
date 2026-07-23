import { createHmac, randomBytes, timingSafeEqual } from "node:crypto";

function jsonError(res, status, error) {
  return res.status(status).json({ error });
}

function asSecret(value) {
  return Buffer.isBuffer(value) ? value : Buffer.from(String(value));
}

export function createSecurity({ authAdapter = null, csrfSecret = process.env.SEVERITY_CSRF_SECRET || randomBytes(32) } = {}) {
  const secret = asSecret(csrfSecret);

  function requireRole(...allowedRoles) {
    return async (req, res, next) => {
      if (!authAdapter) return next();
      try {
        const session = await authAdapter.verify(req.headers.cookie);
        if (!session) return jsonError(res, 401, "Authentication required");
        if (!allowedRoles.some(role => session.roles.includes(role))) {
          return jsonError(res, 403, "Forbidden");
        }
        req.auth = session;
        return next();
      } catch {
        return jsonError(res, 503, "Authentication service unavailable");
      }
    };
  }

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
    return signature.length === expected.length && timingSafeEqual(
      Buffer.from(signature), Buffer.from(expected),
    );
  }

  function issueToken(req, res) {
    const token = mint();
    res.setHeader("Set-Cookie", `csrf=${token}; Path=/; SameSite=Lax`);
    return res.json({ token });
  }

  function requireCsrf(req, res, next) {
    if (!authAdapter) return next();
    const cookie = (req.headers.cookie || "").split(";")
      .map(part => part.trim())
      .find(part => part.startsWith("csrf="))
      ?.slice("csrf=".length);
    const header = req.get("x-csrf-token");
    if (!cookie || !header || cookie !== header || !validToken(cookie)) {
      return jsonError(res, 403, "CSRF token missing or invalid");
    }
    return next();
  }

  return {
    authConfigured: Boolean(authAdapter),
    csrfConfigured: true,
    issueToken,
    requireCsrf,
    requireRole,
    verifyCsrf: validToken,
  };
}
