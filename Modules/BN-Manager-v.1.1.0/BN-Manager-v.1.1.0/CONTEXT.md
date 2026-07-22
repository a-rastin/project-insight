# BN Manager Context

BN Manager contract 2.0.0 is an XML-only clinical Bayesian Network boundary for Dashboard, Add New Patient, and Follow-up. It owns four BIF 0.3 networks: Pharmacotherapy, Treatment Setting, Involuntary Treatment Considerations, and Clozapine in Suicide Risk.

The module registry is the sole file-loading boundary. Registry paths must remain relative to `bn_manager_backend/model_registry/`; caller-controlled filesystem paths are rejected. `XSD.xml` is the canonical structural schema. `validate_model()` supplies semantic checks that XSD cannot express.

All canonical target nodes are chance nodes. Evaluation therefore returns posterior probabilities. The request field `decision_id` remains as a compatibility key, but its values select one of the four model targets.

The Treatment Setting and Involuntary Treatment Considerations files include compact neutral conditional rows. The compiler broadcasts a one-row conditional distribution across all parent combinations and records `table_broadcast=True` on that potential. This behavior is intentionally narrow: it applies only when a conditional table contains exactly one complete child-state row.

Legacy `.net`, `.xmlbif`, the browser workbench, and the model conversion endpoint are outside contract 2.0.0.
