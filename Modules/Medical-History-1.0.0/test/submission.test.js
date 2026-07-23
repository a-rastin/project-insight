const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs/promises");
const os = require("node:os");
const path = require("node:path");
const {
  MedicalHistorySubmissionStore,
  structureCondition,
  structureMedication,
  unresolvedCoding,
} = require("../medical-history-submission.js");

const patientId = "11111111-1111-4111-8111-111111111111";
const encounterId = "22222222-2222-4222-8222-222222222222";

test("structures conditions with original text and explicit unresolved coding", () => {
  assert.deepEqual(structureCondition("Hypertension"), {
    originalText: "Hypertension",
    coding: unresolvedCoding("Hypertension"),
  });
  assert.deepEqual(
    structureCondition({
      originalText: "Asthma",
      coding: {
        system: "http://snomed.info/sct",
        code: "195967001",
        display: "Asthma",
        resolutionStatus: "approved",
      },
    }),
    {
      originalText: "Asthma",
      coding: {
        system: "http://snomed.info/sct",
        code: "195967001",
        display: "Asthma",
        resolutionStatus: "approved",
      },
    },
  );
  assert.equal(structureCondition({ originalText: "Other" }).coding.resolutionStatus, "unresolved");
  assert.equal(structureCondition({ originalText: "Other" }).coding.system, null);
  assert.equal(structureCondition({ originalText: "Other" }).coding.code, null);
});

test("structures medications with original text, RxNorm, dose amount/unit, route, and frequency", () => {
  assert.deepEqual(
    structureMedication({
      name: "Lithium",
      dose: "300 mg",
      route: "Oral",
      frequency: "Daily",
    }),
    {
      originalText: "Lithium",
      rxNorm: {
        system: null,
        code: null,
        display: "Lithium",
        resolutionStatus: "unresolved",
      },
      doseAmount: null,
      doseUnit: null,
      dose: "300 mg",
      route: "Oral",
      frequency: "Daily",
    },
  );
  assert.deepEqual(
    structureMedication({
      originalText: "Sertraline",
      rxNorm: {
        system: "http://www.nlm.nih.gov/research/umls/rxnorm",
        code: "36437",
        display: "sertraline",
        resolutionStatus: "approved",
      },
      doseAmount: 50,
      doseUnit: "mg",
      route: "Oral",
      frequency: "Daily",
    }),
    {
      originalText: "Sertraline",
      rxNorm: {
        system: "http://www.nlm.nih.gov/research/umls/rxnorm",
        code: "36437",
        display: "sertraline",
        resolutionStatus: "approved",
      },
      doseAmount: 50,
      doseUnit: "mg",
      dose: "",
      route: "Oral",
      frequency: "Daily",
    },
  );
});

test("creates a versioned submission resource with identity metadata", async () => {
  const dataDir = await fs.mkdtemp(path.join(os.tmpdir(), "medical-history-submission-"));
  const store = new MedicalHistorySubmissionStore({
    filePath: path.join(dataDir, "submissions.json"),
    now: () => new Date("2026-07-23T12:00:00.000Z"),
  });

  const submission = await store.create({
    patientId,
    encounterId,
    author: "clinician-1",
    data: { pastMedicalHistory: ["Hypertension"] },
  });

  assert.match(submission.id, /^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/);
  assert.equal(submission.submissionId, submission.id);
  assert.equal(submission.patientId, patientId);
  assert.equal(submission.encounterId, encounterId);
  assert.equal(submission.schemaVersion, "1.0.0");
  assert.equal(submission.author, "clinician-1");
  assert.equal(submission.status, "submitted");
  assert.equal(submission.createdAt, "2026-07-23T12:00:00.000Z");
  assert.equal(submission.updatedAt, submission.createdAt);
  assert.equal(submission.submittedAt, submission.createdAt);
  assert.match(submission.etag, /^"[^"]+"$/);
  assert.equal(submission.version, 1);
  assert.deepEqual(submission.data, { pastMedicalHistory: ["Hypertension"] });
  assert.deepEqual(submission.pastMedicalHistory, submission.data.pastMedicalHistory);

  await fs.rm(dataDir, { recursive: true, force: true });
});

test("latest lookup does not replace immutable history", async () => {
  const dataDir = await fs.mkdtemp(path.join(os.tmpdir(), "medical-history-submission-"));
  let tick = 0;
  const store = new MedicalHistorySubmissionStore({
    filePath: path.join(dataDir, "submissions.json"),
    now: () => new Date(`2026-07-23T12:00:0${tick++}.000Z`),
  });

  const first = await store.create({ patientId, encounterId, author: "clinician-1", data: { answer: "first" } });
  const second = await store.create({ patientId, encounterId, author: "clinician-1", data: { answer: "second" } });

  assert.equal((await store.getLatest({ patientId, encounterId })).id, second.id);
  assert.deepEqual((await store.getHistory({ patientId, encounterId })).map((item) => item.id), [first.id, second.id]);
  assert.equal((await store.findById(first.id)).data.answer, "first");
  assert.equal(typeof store.update, "undefined");

  await fs.rm(dataDir, { recursive: true, force: true });
});
