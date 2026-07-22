"""THROWAWAY TP-04 lifecycle prototype. Not for clinical use or production import."""
from copy import deepcopy

class TransitionError(ValueError): pass

REQUIRED_INPUTS = ("diagnosis", "medical_history", "severity", "patient_id", "encounter_id")
EDIT_FIELDS = {"setting", "drug", "dose", "appointment"}
MUTABLE_STATES = {"generated", "editing", "ready_for_review"}

def initial_state():
    return {"status": "requested", "inputs": {}, "missing_inputs": list(REQUIRED_INPUTS),
            "plan": {key: None for key in EDIT_FIELDS}, "edits": [], "ddi_findings": [],
            "overrides": [], "finalized_plan": None, "follow_up_delta": None, "successor": None}

def reduce(state, action):
    """Return a new state for one action; never mutate ``state``."""
    result, kind = deepcopy(state), action.get("type")
    if kind == "gather_inputs":
        _require(result["status"] in {"requested", "inputs_incomplete"}, result, kind)
        result["inputs"] = deepcopy(action.get("inputs", {}))
        result["missing_inputs"] = [key for key in REQUIRED_INPUTS if not result["inputs"].get(key)]
        result["status"] = "inputs_incomplete" if result["missing_inputs"] else "evaluating"
    elif kind == "generate":
        _require(result["status"] == "evaluating", result, kind)
        missing = sorted(EDIT_FIELDS - action.get("plan", {}).keys())
        if missing: raise TransitionError("generated plan is missing fields: " + ", ".join(missing))
        result["plan"] = {key: deepcopy(action["plan"][key]) for key in sorted(EDIT_FIELDS)}
        result["status"] = "generated"
    elif kind == "edit":
        _require(result["status"] in MUTABLE_STATES, result, kind)
        field = action.get("field")
        if field not in EDIT_FIELDS: raise TransitionError(f"unknown editable field: {field!r}")
        if action.get("value") in (None, ""): raise TransitionError(f"{field} cannot be blank")
        before = deepcopy(result["plan"][field]); result["plan"][field] = deepcopy(action["value"])
        result["edits"].append({"field": field, "before": before, "after": deepcopy(action["value"])})
        result["status"] = "editing"
    elif kind == "record_ddi":
        _require(result["status"] in MUTABLE_STATES, result, kind)
        if action.get("severity") not in {"low", "moderate", "high"}: raise TransitionError("DDI severity must be low, moderate, or high")
        finding_id = action.get("finding_id")
        if not finding_id or any(x["finding_id"] == finding_id for x in result["ddi_findings"]): raise TransitionError("DDI finding_id must be nonblank and unique")
        result["ddi_findings"].append({"finding_id": finding_id, "severity": action["severity"], "description": action.get("description", "")})
        result["status"] = "editing"
    elif kind == "override_ddi":
        _require(result["status"] in MUTABLE_STATES, result, kind)
        finding = next((x for x in result["ddi_findings"] if x["finding_id"] == action.get("finding_id")), None)
        if not finding: raise TransitionError("override must reference an existing DDI finding")
        if finding["severity"] != "high": raise TransitionError("only high-severity DDI findings use controlled override")
        if any(x["finding_id"] == finding["finding_id"] for x in result["overrides"]): raise TransitionError("DDI finding is already overridden")
        reason, actor = str(action.get("reason", "")).strip(), str(action.get("actor", "")).strip()
        if not reason or not actor: raise TransitionError("high-severity DDI override requires nonblank reason and actor")
        result["overrides"].append({"finding_id": finding["finding_id"], "reason": reason, "actor": actor}); result["status"] = "editing"
    elif kind == "submit_for_review":
        _require(result["status"] in {"generated", "editing"}, result, kind); result["status"] = "ready_for_review"
    elif kind == "finalize":
        _require(result["status"] == "ready_for_review", result, kind)
        overridden = {x["finding_id"] for x in result["overrides"]}
        blocked = [x["finding_id"] for x in result["ddi_findings"] if x["severity"] == "high" and x["finding_id"] not in overridden]
        if blocked: raise TransitionError("finalization blocked by high-severity DDI: " + ", ".join(blocked))
        result["finalized_plan"], result["status"] = deepcopy(result["plan"]), "finalized"
    elif kind == "apply_follow_up_delta":
        _require(result["status"] == "finalized", result, kind)
        if not isinstance(action.get("delta"), dict) or not action["delta"]: raise TransitionError("follow-up delta must be a non-empty mapping")
        result["follow_up_delta"] = deepcopy(action["delta"])
    elif kind == "supersede":
        _require(result["status"] == "finalized", result, kind)
        if result["follow_up_delta"] is None: raise TransitionError("supersession requires a follow-up delta")
        result["successor"] = {"status": "requested", "based_on": deepcopy(result["finalized_plan"]), "follow_up_delta": deepcopy(result["follow_up_delta"])}
        result["status"] = "superseded"
    else: raise TransitionError(f"unknown action: {kind!r}")
    return result

def _require(condition, state, action):
    if not condition: raise TransitionError(f"{action} is illegal while status is {state['status']}")
