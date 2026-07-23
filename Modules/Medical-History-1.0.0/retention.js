const REQUIRED_APPROVER_ROLES = Object.freeze(["privacy_officer", "clinical_safety_officer"]);

class RetentionApprovalRequired extends Error {
  constructor(message) {
    super(message);
    this.name = "RetentionApprovalRequired";
    this.status = 403;
  }
}

function assertRetentionPolicy(policy, now = new Date()) {
  if (!policy || typeof policy !== "object") {
    throw new RetentionApprovalRequired("retention policy is required");
  }
  if (typeof policy.policyId !== "string" || policy.policyId.trim() === "") {
    throw new RetentionApprovalRequired("retention policy identifier is required");
  }
  const roles = new Set((policy.approverRoles || []).map((role) => String(role).trim()).filter(Boolean));
  for (const required of REQUIRED_APPROVER_ROLES) {
    if (!roles.has(required)) {
      throw new RetentionApprovalRequired(`retention policy requires approval role: ${required}`);
    }
  }
  const approvedAt = new Date(policy.approvedAt);
  if (!Number.isFinite(approvedAt.getTime())) {
    throw new RetentionApprovalRequired("retention approval time must be a valid timestamp");
  }
  if (approvedAt.getTime() > now.getTime()) {
    throw new RetentionApprovalRequired("retention policy approval cannot be in the future");
  }
  return {
    policyId: policy.policyId.trim(),
    approverRoles: [...roles],
    approvedAt: approvedAt.toISOString(),
  };
}

function applyRetentionPolicy(repository, { policy, now = new Date(), retentionDays } = {}) {
  const approved = assertRetentionPolicy(policy, now);
  const days = Number(retentionDays ?? process.env.MEDICAL_HISTORY_PHI_RETENTION_DAYS);
  if (!Number.isFinite(days) || days <= 0) {
    throw new RetentionApprovalRequired("MEDICAL_HISTORY_PHI_RETENTION_DAYS must be a positive number");
  }
  const cutoff = new Date(now.getTime() - days * 24 * 60 * 60 * 1000);
  const result = repository.applyRetention({
    cutoffIso: cutoff.toISOString(),
    redactedAtIso: now.toISOString(),
  });
  if (typeof repository.appendAudit === "function") {
    repository.appendAudit({
      action: "retention.apply",
      actor: "retention-job",
      role: approved.approverRoles.join(","),
      detail: {
        policyId: approved.policyId,
        cutoff: cutoff.toISOString(),
        ...result,
      },
      createdAt: now.toISOString(),
    });
  }
  return { ...result, policyId: approved.policyId, cutoff: cutoff.toISOString() };
}

module.exports = {
  REQUIRED_APPROVER_ROLES,
  RetentionApprovalRequired,
  assertRetentionPolicy,
  applyRetentionPolicy,
};
