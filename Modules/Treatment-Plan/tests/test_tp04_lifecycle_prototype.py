import copy, sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[1] / "prototype"))
from treatment_plan_lifecycle import TransitionError, initial_state, reduce
INPUTS={k:f"synthetic-{k}" for k in ("diagnosis","medical_history","severity","patient_id","encounter_id")}
PLAN={"setting":"outpatient","drug":"drug-a","dose":"dose-a","appointment":"interval-a"}
def generated(): return reduce(reduce(initial_state(),{"type":"gather_inputs","inputs":INPUTS}),{"type":"generate","plan":PLAN})
class LifecyclePrototypeTests(unittest.TestCase):
 def test_reducer_is_pure(self):
  state=initial_state(); original=copy.deepcopy(state); reduce(state,{"type":"gather_inputs","inputs":INPUTS}); self.assertEqual(original,state)
 def test_incomplete_inputs_block_generation(self):
  state=reduce(initial_state(),{"type":"gather_inputs","inputs":{"patient_id":"p"}}); self.assertEqual("inputs_incomplete",state["status"])
  with self.assertRaisesRegex(TransitionError,"generate is illegal"): reduce(state,{"type":"generate","plan":PLAN})
 def test_each_structured_edit_is_recorded(self):
  state=generated()
  for field in ("setting","drug","dose","appointment"): state=reduce(state,{"type":"edit","field":field,"value":f"changed-{field}"})
  self.assertEqual(4,len(state["edits"])); self.assertEqual("editing",state["status"])
 def test_high_ddi_needs_override(self):
  state=reduce(generated(),{"type":"record_ddi","finding_id":"d1","severity":"high"})
  with self.assertRaisesRegex(TransitionError,"nonblank reason and actor"): reduce(state,{"type":"override_ddi","finding_id":"d1","reason":" ","actor":"doctor"})
  state=reduce(state,{"type":"submit_for_review"})
  with self.assertRaisesRegex(TransitionError,"blocked"): reduce(state,{"type":"finalize"})
 def test_override_finalizes_but_final_is_immutable(self):
  state=reduce(generated(),{"type":"record_ddi","finding_id":"d1","severity":"high"}); state=reduce(state,{"type":"override_ddi","finding_id":"d1","reason":"synthetic rationale","actor":"doctor"}); state=reduce(reduce(state,{"type":"submit_for_review"}),{"type":"finalize"})
  with self.assertRaisesRegex(TransitionError,"edit is illegal"): reduce(state,{"type":"edit","field":"dose","value":"new"})
 def test_follow_up_delta_required_to_supersede(self):
  state=reduce(reduce(generated(),{"type":"submit_for_review"}),{"type":"finalize"})
  with self.assertRaisesRegex(TransitionError,"requires a follow-up delta"): reduce(state,{"type":"supersede"})
  state=reduce(state,{"type":"apply_follow_up_delta","delta":{"encounter_id":"next"}}); state=reduce(state,{"type":"supersede"}); self.assertEqual("superseded",state["status"])
if __name__ == "__main__": unittest.main()
