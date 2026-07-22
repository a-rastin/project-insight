# BN Manager Ubiquitous Language

**Canonical XML BN**: One of the four module-owned BIF 0.3 `.xml` Bayesian Networks.

**Registry Entry**: Stable metadata binding a model ID, title, relative XML path, target node, version, status, and schema path.

**Target Node**: The chance node whose posterior distribution is returned to a clinical surface.

**Evidence**: Hard state observations or uncertain state weights supplied by a caller.

**Posterior Evaluation**: Exact Bayesian inference returning normalized probabilities for every target state.

**Structural Validation**: Validation of XML shape, required elements, node-key references, and minimum outcomes against `XSD.xml`.

**Semantic Validation**: Checks over the compiled graph, including references, state uniqueness, CPT width, probability row sums, missing potentials, and target existence.

**Compact CPT Row**: A single complete child-state distribution attached to a conditional node. BN Manager broadcasts it across all parent-state combinations and marks the potential as broadcast.

**Clinical Safety Boundary**: BN Manager output is decision support requiring licensed-clinician review; it is not a diagnosis, prescription, or treatment order.

**Module Boundary**: Callers use BN Manager HTTP routes. BN Manager does not import Dashboard, patient databases, or other clinical surfaces.
