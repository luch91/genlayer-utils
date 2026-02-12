# { "Depends": "py-genlayer:test" }
#
# Fact Checker — Example GenLayer Intelligent Contract
# Uses: nondet, llm, access_control, storage helpers from genlayer-utils
#
# A simplified fact-checking contract where users submit claims,
# and AI verifies them against web sources.

import json
from dataclasses import dataclass
from genlayer import *


# ─── genlayer-utils: nondet ─────────────────────────────────────────────────

def web_llm_strict(url, prompt_template, *, mode="text", response_format="json"):
    def _inner():
        web_data = gl.nondet.web.render(url, mode=mode)
        filled_prompt = prompt_template.format(web_data=web_data)
        result = gl.nondet.exec_prompt(filled_prompt, response_format=response_format)
        if isinstance(result, dict):
            return json.dumps(result, sort_keys=True)
        return result
    raw = gl.eq_principle.strict_eq(_inner)
    if response_format == "json":
        return json.loads(raw)
    return raw


# ─── genlayer-utils: llm ────────────────────────────────────────────────────

def fact_check_prompt(claim, evidence, verdicts=None):
    if verdicts is None:
        verdicts = ["true", "false", "partially_true"]
    v = "|".join(verdicts)
    return f"""You are a fact-checker. Based on the evidence provided,
determine whether the following claim is {" or ".join(verdicts)}.

CLAIM: {claim}

EVIDENCE:
{evidence}

Respond ONLY with this exact JSON format, nothing else:
{{"verdict": "<{v}>", "explanation": "<brief 1-2 sentence explanation>"}}

Rules:
- Base your verdict strictly on the provided evidence
- Keep the explanation concise and factual
- Your response must be valid JSON only, no extra text"""


# ─── genlayer-utils: access_control ─────────────────────────────────────────

def require_sender(expected):
    if gl.message.sender_address != expected:
        raise Exception("Unauthorized: caller is not the expected address")


# ─── genlayer-utils: storage ────────────────────────────────────────────────

def increment_or_init(data, key, amount=1):
    current = data.get(key, 0)
    data[key] = current + amount


def address_map_to_dict(data):
    return {k.as_hex: v for k, v in data.items()}


# ─── Contract ───────────────────────────────────────────────────────────────

@allow_storage
@dataclass
class Claim:
    id: str
    text: str
    source_url: str
    submitter: str
    verdict: str
    explanation: str
    is_resolved: bool


class FactChecker(gl.Contract):
    claims: TreeMap[str, Claim]
    reputation: TreeMap[Address, u256]
    claim_count: u256
    _owner: Address

    def __init__(self):
        self.claim_count = 0
        self._owner = gl.message.sender_address

    @gl.public.write
    def submit_claim(self, claim_text: str, source_url: str) -> None:
        self.claim_count += 1
        claim_id = f"claim_{self.claim_count}"

        self.claims[claim_id] = Claim(
            id=claim_id,
            text=claim_text,
            source_url=source_url,
            submitter=gl.message.sender_address.as_hex,
            verdict="pending",
            explanation="",
            is_resolved=False,
        )

    @gl.public.write
    def resolve_claim(self, claim_id: str) -> None:
        if claim_id not in self.claims:
            raise Exception("Claim not found")

        claim = self.claims[claim_id]
        if claim.is_resolved:
            raise Exception("Claim already resolved")

        # genlayer-utils makes this 2 lines instead of 20
        prompt = fact_check_prompt(claim.text, "{web_data}")
        result = web_llm_strict(url=claim.source_url, prompt_template=prompt)

        claim.verdict = result["verdict"]
        claim.explanation = result.get("explanation", "")
        claim.is_resolved = True

        # Award reputation to submitter
        increment_or_init(self.reputation, Address(claim.submitter))

    @gl.public.write
    def delete_claim(self, claim_id: str) -> None:
        require_sender(self._owner)
        if claim_id in self.claims:
            del self.claims[claim_id]

    @gl.public.view
    def get_claim(self, claim_id: str) -> dict:
        if claim_id not in self.claims:
            raise Exception("Claim not found")
        c = self.claims[claim_id]
        return {
            "id": c.id, "text": c.text, "source_url": c.source_url,
            "submitter": c.submitter, "verdict": c.verdict,
            "explanation": c.explanation, "is_resolved": c.is_resolved,
        }

    @gl.public.view
    def get_all_claims(self) -> list:
        return [
            {"id": c.id, "text": c.text, "verdict": c.verdict, "is_resolved": c.is_resolved}
            for _, c in self.claims.items()
        ]

    @gl.public.view
    def get_reputation(self) -> dict:
        return address_map_to_dict(self.reputation)
