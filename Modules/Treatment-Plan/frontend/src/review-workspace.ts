export type SafetyLevel = "urgent" | "warning" | "info";
export type Dose = { amount: string; unit: string };
export type MedicationRecommendation = { name: string; code: string; dose: Dose; route: string; frequency: string };
export type PlanValues = { setting: string; medication: MedicationRecommendation; followUp: { amount: string; unit: string } };
export type ReviewField =
  | "setting"
  | "medication.name"
  | "medication.code"
  | "medication.dose.amount"
  | "medication.dose.unit"
  | "medication.route"
  | "medication.frequency"
  | "followUp.amount"
  | "followUp.unit";

export type ReviewCase = {
  patient: { displayId: string; ageBand: string; encounterLabel: string };
  dataWarnings: Array<{ id: string; title: string; detail: string; stale?: boolean }>;
  recommendation: PlanValues;
  rationale: string[];
  alternatives: Array<{ name: string; summary: string; reason: string }>;
  safetyFindings: Array<{ id: string; level: SafetyLevel; title: string; detail: string }>;
  provenance: { modelVersion: string; policyVersion: string; knowledgeVersion: string };
};

type Comparison = { recommended: string; edited: string; changed: boolean };
export type ReviewWorkspace = ReviewCase & {
  recommended: PlanValues;
  draft: PlanValues;
  comparisons: Record<ReviewField, Comparison>;
  urgentFindings: ReviewCase["safetyFindings"];
};

const fields: ReviewField[] = [
  "setting", "medication.name", "medication.code", "medication.dose.amount", "medication.dose.unit",
  "medication.route", "medication.frequency", "followUp.amount", "followUp.unit",
];

function clonePlan(values: PlanValues): PlanValues {
  return {
    setting: values.setting,
    medication: {
      name: values.medication.name,
      code: values.medication.code,
      dose: { amount: values.medication.dose.amount, unit: values.medication.dose.unit },
      route: values.medication.route,
      frequency: values.medication.frequency,
    },
    followUp: { amount: values.followUp.amount, unit: values.followUp.unit },
  };
}

function readField(values: PlanValues, field: ReviewField): string {
  return field.split(".").reduce<unknown>((value, key) => (value as Record<string, unknown>)[key], values) as string;
}

function writeField(values: PlanValues, field: ReviewField, nextValue: string): PlanValues {
  const copy = clonePlan(values);
  const path = field.split(".");
  const leaf = path.pop()!;
  const parent = path.reduce<Record<string, unknown>>(
    (value, key) => value[key] as Record<string, unknown>,
    copy as unknown as Record<string, unknown>,
  );
  parent[leaf] = nextValue;
  return copy;
}

function compare(recommended: PlanValues, draft: PlanValues): Record<ReviewField, Comparison> {
  return Object.fromEntries(fields.map((field) => {
    const original = readField(recommended, field);
    const edited = readField(draft, field);
    return [field, { recommended: original, edited, changed: original !== edited }];
  })) as Record<ReviewField, Comparison>;
}

export function createReviewWorkspace(reviewCase: ReviewCase): ReviewWorkspace {
  const recommended = clonePlan(reviewCase.recommendation);
  const draft = clonePlan(reviewCase.recommendation);
  return {
    ...reviewCase,
    recommended,
    draft,
    comparisons: compare(recommended, draft),
    urgentFindings: reviewCase.safetyFindings.filter((finding) => finding.level === "urgent"),
  };
}

export function updateReviewField(workspace: ReviewWorkspace, field: ReviewField, value: string): ReviewWorkspace {
  const draft = writeField(workspace.draft, field, value);
  return { ...workspace, draft, comparisons: compare(workspace.recommended, draft) };
}
