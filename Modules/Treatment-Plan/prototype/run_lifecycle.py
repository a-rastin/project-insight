"""Run: python prototype/run_lifecycle.py (synthetic walkthrough only)."""
import json
from treatment_plan_lifecycle import TransitionError, initial_state, reduce

INPUTS = {"patient_id":"synthetic-patient","encounter_id":"synthetic-encounter","diagnosis":"synthetic-diagnosis","medical_history":"synthetic-history","severity":"synthetic-severity"}
PLAN = {"setting":"outpatient","drug":"synthetic-drug-a","dose":"synthetic-dose-a","appointment":"synthetic-interval-a"}
def baseline(): return [{"type":"gather_inputs","inputs":INPUTS},{"type":"generate","plan":PLAN}]
SCENARIOS = [
 ("1 incomplete inputs block generation", [{"type":"gather_inputs","inputs":{"patient_id":"synthetic-patient"}},{"type":"generate","plan":PLAN}]),
 ("2 complete inputs generate and finalize", baseline()+[{"type":"submit_for_review"},{"type":"finalize"}]),
 ("3 all structured edits", baseline()+[{"type":"edit","field":f,"value":f"synthetic-{f}-b"} for f in ("setting","drug","dose","appointment")]+[{"type":"submit_for_review"},{"type":"finalize"}]),
 ("4 high DDI blocks finalization", baseline()+[{"type":"record_ddi","finding_id":"ddi-high-1","severity":"high","description":"synthetic interaction"},{"type":"submit_for_review"},{"type":"finalize"}]),
 ("5 invalid then valid override", baseline()+[{"type":"record_ddi","finding_id":"ddi-high-1","severity":"high"},{"type":"override_ddi","finding_id":"ddi-high-1","reason":"","actor":"synthetic-psychiatrist"},{"type":"override_ddi","finding_id":"ddi-high-1","reason":"synthetic rationale","actor":"synthetic-psychiatrist"},{"type":"submit_for_review"},{"type":"finalize"}]),
 ("6 follow-up supersession and immutable old plan", baseline()+[{"type":"submit_for_review"},{"type":"finalize"},{"type":"apply_follow_up_delta","delta":{"encounter_id":"synthetic-follow-up","severity":"changed"}},{"type":"supersede"},{"type":"edit","field":"dose","value":"illegal"}]),
]
def main():
    print("THROWAWAY RESEARCH PROTOTYPE - SYNTHETIC DATA ONLY - NOT FOR CLINICAL USE")
    for name, actions in SCENARIOS:
        state=initial_state(); print(f"\n=== {name} ===\nINITIAL\n{json.dumps(state,indent=2,sort_keys=True)}")
        for action in actions:
            error=None
            try: state=reduce(state,action)
            except TransitionError as exc: error=str(exc)
            print(f"\nACTION\n{json.dumps(action,indent=2,sort_keys=True)}")
            if error: print(f"REJECTED: {error}")
            print(f"STATE\n{json.dumps(state,indent=2,sort_keys=True)}")
if __name__ == "__main__": main()
