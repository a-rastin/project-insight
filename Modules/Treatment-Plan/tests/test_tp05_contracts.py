import copy, json, sys, unittest
from pathlib import Path
ROOT=Path(__file__).parents[1]; sys.path.insert(0,str(ROOT/"scripts"))
from check_tp05_contracts import ContractError, check_compatibility, lint_openapi, load, schema_for, validate, validate_examples

class TP05ContractTests(unittest.TestCase):
    def test_all_examples_validate(self): validate_examples()
    def test_openapi_lints(self): lint_openapi()
    def test_backward_compatibility_corpus(self): check_compatibility()
    def test_unknown_safety_relevant_clinical_field_is_rejected(self):
        name="clinical-input-snapshot"; example=load(ROOT/"contracts"/"examples"/"1.0.0"/f"{name}.json")
        example["diagnosis"]["unreviewedGuess"]="unsafe"
        with self.assertRaisesRegex(ContractError,"unknown properties"): validate(example,load(schema_for("1.0.0",name)),schema_for("1.0.0",name))
    def test_malformed_clinical_field_is_rejected(self):
        name="clinical-input-snapshot"; example=load(ROOT/"contracts"/"examples"/"1.0.0"/f"{name}.json")
        example["diagnosis"]["codeSystem"]="free-text"
        with self.assertRaisesRegex(ContractError,"enum"): validate(example,load(schema_for("1.0.0",name)),schema_for("1.0.0",name))
    def test_wrong_schema_version_is_rejected(self):
        name="primary-plan"; example=load(ROOT/"contracts"/"examples"/"1.0.0"/f"{name}.json"); example["schemaVersion"]="1.1.0"
        with self.assertRaises(ContractError): validate(example,load(schema_for("1.0.0",name)),schema_for("1.0.0",name))

if __name__=="__main__": unittest.main()
