# Test: Fact Checker example contract
#
# Run with: gltest (GenLayer Studio must be running)
#
# These tests deploy the fact_checker.py example and verify
# the core flow: submit a claim, resolve it with AI, check results.

from gltest import get_contract_factory, default_account
from gltest.helpers import load_fixture
from gltest.assertions import tx_execution_succeeded


def deploy_contract():
    factory = get_contract_factory("FactChecker", path="examples/fact_checker.py")
    contract = factory.deploy()
    return contract


def test_submit_claim():
    """Test that a claim can be submitted successfully."""
    contract = load_fixture(deploy_contract)

    result = contract.submit_claim(
        args=[
            "Python was created by Guido van Rossum",
            "https://en.wikipedia.org/wiki/Python_(programming_language)",
        ]
    )
    assert tx_execution_succeeded(result)

    # Verify the claim exists
    claim = contract.get_claim(args=["claim_1"])
    assert claim["text"] == "Python was created by Guido van Rossum"
    assert claim["verdict"] == "pending"
    assert claim["is_resolved"] == False


def test_resolve_claim():
    """Test that a claim can be resolved via AI fact-checking."""
    contract = load_fixture(deploy_contract)

    # Submit first
    contract.submit_claim(
        args=[
            "Python was created by Guido van Rossum",
            "https://en.wikipedia.org/wiki/Python_(programming_language)",
        ]
    )

    # Resolve (triggers web fetch + LLM + consensus)
    result = contract.resolve_claim(
        args=["claim_1"],
        wait_interval=10000,
        wait_retries=15,
    )
    assert tx_execution_succeeded(result)

    # Verify verdict
    claim = contract.get_claim(args=["claim_1"])
    assert claim["is_resolved"] == True
    assert claim["verdict"] in ["true", "false", "partially_true"]
    assert len(claim["explanation"]) > 0


def test_get_all_claims():
    """Test listing all claims."""
    contract = load_fixture(deploy_contract)

    contract.submit_claim(args=["Claim one", "https://example.com"])
    contract.submit_claim(args=["Claim two", "https://example.com"])

    claims = contract.get_all_claims(args=[])
    assert len(claims) == 2


def test_owner_delete():
    """Test that the owner can delete claims."""
    contract = load_fixture(deploy_contract)

    contract.submit_claim(args=["Test claim", "https://example.com"])
    result = contract.delete_claim(args=["claim_1"])
    assert tx_execution_succeeded(result)
