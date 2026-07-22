import unittest
from datetime import datetime,timedelta,timezone
from treatment_plan.clinical_context import ClinicalContext,ContextError,ContextErrorCode,Dependency
from treatment_plan.eligibility import Blocker,Eligibility,GenerationEligibilityPolicy
NOW=datetime(2026,7,13,12,tzinfo=timezone.utc); PATHWAY="schizophrenia-research-v1"
def context(*,omit=None,pending=False,stale_history=False,unresolved_medication=False,suicide_risk=None,unavailable=None):
 base={"observedAt":NOW.isoformat()}; inputs={
 Dependency.PATIENT:{**base,"currentMedications":[{"status":"unresolved"}] if unresolved_medication else []},
 Dependency.DIAGNOSIS:{**base,"diagnosis":{"code":"F20.9"}},
 Dependency.SEVERITY:{**base,"status":"pending" if pending else "complete","severity":{"score":12}},
 Dependency.MEDICAL_HISTORY:{**base,"medicalHistory":{}},Dependency.DDI:{**base,"findings":[]},Dependency.BN:{**base,"evaluation":{}}}
 if stale_history:inputs[Dependency.MEDICAL_HISTORY]["observedAt"]=(NOW-timedelta(days=31)).isoformat()
 if suicide_risk is not None:inputs[Dependency.SEVERITY]["severity"]["suicideRisk"]=suicide_risk
 if omit:inputs.pop(omit)
 findings=()
 if unavailable:
  inputs.pop(unavailable,None);findings=(ContextError(unavailable,ContextErrorCode.UNAVAILABLE,"outage",True),)
 return ClinicalContext("patient","encounter",inputs,(),findings)
class TP09EligibilityPolicyTests(unittest.TestCase):
 def test_acceptance_scenarios_are_table_driven(self):
  cases=(("missing diagnosis",context(omit=Dependency.DIAGNOSIS),Eligibility.BLOCKED,"required-fact-missing",Blocker.HARD),("pending severity",context(pending=True),Eligibility.BLOCKED,"severity-pending",Blocker.HARD),("stale history",context(stale_history=True),Eligibility.ELIGIBLE,"stale-fact",Blocker.SOFT),("unresolved medication",context(unresolved_medication=True),Eligibility.BLOCKED,"medication-unresolved",Blocker.HARD),("contradictory suicide risk",context(suicide_risk=["low","high"]),Eligibility.SAFETY_PATHWAY,"suicide-risk-contradiction",Blocker.SAFETY),("BN unavailable",context(unavailable=Dependency.BN),Eligibility.BLOCKED,"source-unavailable",Blocker.HARD),("DDI unavailable",context(unavailable=Dependency.DDI),Eligibility.BLOCKED,"source-unavailable",Blocker.HARD))
  evaluator=GenerationEligibilityPolicy()
  for name,ctx,outcome,code,blocker in cases:
   with self.subTest(name=name):
    decision=evaluator.evaluate(ctx,PATHWAY,now=NOW);self.assertEqual(decision.eligibility,outcome);self.assertIn((code,blocker),{(x.code,x.blocker) for x in decision.findings});self.assertEqual(decision.generation_allowed,outcome is Eligibility.ELIGIBLE)
 def test_high_risk_uses_explicit_safety_pathway(self):
  decision=GenerationEligibilityPolicy().evaluate(context(suicide_risk="imminent"),PATHWAY,now=NOW);self.assertEqual(decision.eligibility,Eligibility.SAFETY_PATHWAY);self.assertFalse(decision.generation_allowed)
 def test_unknown_pathway_fails_closed(self):
  with self.assertRaisesRegex(ValueError,"unsupported pathway"):GenerationEligibilityPolicy().evaluate(context(),"unknown",now=NOW)
if __name__=="__main__":unittest.main()
