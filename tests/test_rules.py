"""
tests/test_rules.py

Validates that all rule files are correctly structured.
No glob patterns, no empty lists.
"""

from rules import python_rules, node_rules, java_rules, rust_rules, cpp_rules

RULE_MODULES = [python_rules, node_rules, java_rules, rust_rules, cpp_rules]

def test_all_rules_have_signatures():
    for module in RULE_MODULES:
        assert hasattr(module, "SIGNATURES"), f"{module.__name__} does not have SIGNATURES"
        assert module.SIGNATURES, f"{module.__name__} has empty SIGNATURES"

def test_all_rules_have_deletables():
    for module in RULE_MODULES:
        assert hasattr(module, "DELETABLES"), f"{module.__name__} does not have DELETABLES"
        assert module.DELETABLES, f"{module.__name__} has empty DELETABLES"

def test_no_glob_patterns_in_deletables():
    for module in RULE_MODULES:
        for deletable in module.DELETABLES:
            assert "*" not in deletable, f"{module.__name__} has glob pattern in DELETABLES: {deletable}"

def test_no_glob_patterns_in_reviewables():
    for module in RULE_MODULES:
        for signature in module.REVIEWABLES:
            assert "*" not in signature, f"{module.__name__} has glob pattern in SIGNATURES: {signature}"