// Canonical Authentication session adapter. Cookie forwarded only to allowlisted AUTH_SESSION_URL.

function parseCanonicalSession(payload) {
  if (!payload || payload.schemaVersion !== "1.0.0" || payload.authenticated !== true) return null;
  const { user, session, gates } = payload;
  if (!user || !session || !gates || typeof user !== "object" || typeof session !== "object" || typeof gates !== "object") return null;
  if (gates.disclaimerAccepted !== true || gates.passwordChangeRequired !== false) return null;
  if (typeof user.id !== "string" || !user.id || typeof session.id !== "string" || !session.id) return null;
  if (!Array.isArray(user.roles) || user.roles.some((role) => typeof role !== "string" || role !== role.toLowerCase())) return null;
  const expiresAt = Date.parse(session.expiresAt || "");
  if (!Number.isFinite(expiresAt) || expiresAt <= Date.now()) return null;
  return { userId: user.id, sessionId: session.id, roles: Object.freeze([...user.roles]), expiresAt };
}

function createMemoryAuthAdapter(sessions = new Map()) {
  return {
    async verify(cookieHeader) {
      const token = String(cookieHeader || "")
        .split(";")
        .map((part) => part.trim())
        .find((part) => part.startsWith("insight_session="))
        ?.slice("insight_session=".length);
      return token && sessions.has(token) ? sessions.get(token) : null;
    },
  };
}

function createHttpAuthAdapter({
  sessionUrl = process.env.AUTH_SESSION_URL || "",
  timeoutMs = Number(process.env.AUTH_SESSION_TIMEOUT_MS || 2000),
  fetchImpl = globalThis.fetch,
} = {}) {
  if (!sessionUrl) throw new Error("AUTH_SESSION_URL is required");
  let allowedOrigin;
  try {
    const parsed = new URL(sessionUrl);
    if (!["http:", "https:"].includes(parsed.protocol) || parsed.username || parsed.password) {
      throw new Error("invalid");
    }
    allowedOrigin = parsed.origin;
  } catch {
    throw new Error("AUTH_SESSION_URL must be an absolute http(s) URL");
  }

  return {
    async verify(cookieHeader) {
      if (!cookieHeader) return null;
      const target = new URL(sessionUrl);
      if (target.origin !== allowedOrigin) return null;
      const controller = new AbortController();
      const timer = setTimeout(() => controller.abort(), timeoutMs);
      try {
        const response = await fetchImpl(sessionUrl, {
          method: "GET",
          headers: { accept: "application/json", cookie: cookieHeader },
          signal: controller.signal,
        });
        if (response.status === 401 || response.status === 403) return null;
        if (!response.ok) throw new Error(`Authentication session check failed with ${response.status}`);
        return parseCanonicalSession(await response.json());
      } catch (error) {
        if (error?.name === "AbortError") throw new Error("Authentication session check timed out");
        throw error;
      } finally {
        clearTimeout(timer);
      }
    },
  };
}

module.exports = { parseCanonicalSession, createMemoryAuthAdapter, createHttpAuthAdapter };
