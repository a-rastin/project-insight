export function createReadinessProbe({ assessmentStore, authConfigured, csrfConfigured }) {
  return function readiness() {
    let database = "ok";
    try {
      assessmentStore.read();
    } catch {
      database = "blocked";
    }
    const checks = {
      database,
      authentication: authConfigured ? "ok" : "disabled",
      csrf: csrfConfigured ? "ok" : "blocked",
    };
    const ok = Object.values(checks).every(value => value === "ok" || value === "disabled");
    return { ok, checks };
  };
}
