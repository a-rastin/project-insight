function createReadinessProbe({ repository, authConfigured, csrfConfigured }) {
  return function readiness() {
    let database = "ok";
    try {
      if (!repository.ping()) database = "blocked";
    } catch {
      database = "blocked";
    }
    const checks = {
      database,
      authentication: authConfigured ? "ok" : "disabled",
      csrf: csrfConfigured ? "ok" : "blocked",
    };
    const ok = Object.values(checks).every((value) => value === "ok" || value === "disabled");
    return { ok, module: "medical-history", checks };
  };
}

module.exports = { createReadinessProbe };
