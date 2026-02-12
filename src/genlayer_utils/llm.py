# genlayer-utils: llm.py
# LLM prompt templates and response validators for GenLayer Intelligent Contracts
#
# Pre-built prompt templates optimized for strict_eq consensus: constrained
# output space, JSON format, explicit instructions. Copy the functions you
# need into the top of your contract file.
#
# Requires: from genlayer import *


# =============================================================================
# Prompt Templates
# =============================================================================


def classify_prompt(
    text: str,
    categories: list[str],
    context: str = "",
) -> str:
    """
    Build a prompt that classifies text into one of the given categories.
    Optimized for strict_eq consensus (constrained output space).

    Args:
        text: The text to classify
        categories: List of valid category labels
        context: Optional context or role description

    Returns:
        A formatted prompt string ready for exec_prompt(response_format="json")

    Example:
        prompt = classify_prompt(
            text="This product is terrible, waste of money",
            categories=["positive", "negative", "neutral"],
            context="You are analyzing customer reviews."
        )
        # Use with: llm_strict(prompt) or gl.nondet.exec_prompt(prompt, response_format="json")
    """
    cats = "|".join(categories)
    ctx = f"\nCONTEXT: {context}\n" if context else ""

    return f"""Classify the following text into exactly one category.
{ctx}
TEXT: {text}

CATEGORIES: {cats}

Respond ONLY with this exact JSON format, nothing else:
{{"category": "<{cats}>", "confidence": "<high|medium|low>", "reason": "<1 sentence>"}}

Rules:
- Choose the single best-matching category
- Your response must be valid JSON only, no extra text"""


def extract_prompt(
    text: str,
    fields: dict,
) -> str:
    """
    Build a prompt that extracts structured fields from text.

    Args:
        text: The text to extract information from
        fields: Dict of {field_name: description}

    Returns:
        A formatted prompt string

    Example:
        prompt = extract_prompt(
            text="John Smith, age 32, works at Google as a software engineer",
            fields={"name": "person's full name", "age": "numeric age", "company": "employer"}
        )
    """
    schema = ", ".join(f'"{k}": "<{v}>"' for k, v in fields.items())

    return f"""Extract the following information from the text.

TEXT: {text}

Respond ONLY with this exact JSON format, nothing else:
{{{schema}}}

Rules:
- If a field cannot be determined, use "unknown"
- Your response must be valid JSON only, no extra text"""


def fact_check_prompt(
    claim: str,
    evidence: str,
    verdicts: list[str] | None = None,
) -> str:
    """
    Build a fact-checking prompt. Designed for use with web_llm_strict()
    where evidence contains a {web_data} placeholder.

    Args:
        claim: The claim to fact-check
        evidence: The evidence text (or "{web_data}" placeholder for web_llm_strict)
        verdicts: Valid verdict labels (default: true/false/partially_true)

    Returns:
        A formatted prompt string

    Example:
        prompt = fact_check_prompt(
            claim="Python was created in 1991",
            evidence="{web_data}",  # will be filled by web_llm_strict
            verdicts=["true", "false", "partially_true"]
        )
        result = web_llm_strict(url="https://en.wikipedia.org/wiki/Python", prompt_template=prompt)
    """
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


def yes_no_prompt(question: str, context: str = "") -> str:
    """
    Build a yes/no question prompt. Maximum consensus reliability
    due to minimal output space.

    Args:
        question: The yes/no question to answer
        context: Optional context

    Returns:
        A formatted prompt string

    Example:
        prompt = yes_no_prompt(
            question="Is this website a legitimate news source?",
            context="The website publishes articles about technology."
        )
    """
    ctx = f"\nCONTEXT: {context}\n" if context else ""

    return f"""Answer the following question with yes or no.
{ctx}
QUESTION: {question}

Respond ONLY with this exact JSON format, nothing else:
{{"answer": "<yes|no>", "reason": "<1 sentence>"}}"""


# =============================================================================
# Response Validators
# =============================================================================


def validate_json_fields(result: dict, required_fields: list[str]) -> bool:
    """
    Check that all required fields are present in an LLM response dict.

    Args:
        result: The parsed dict from exec_prompt
        required_fields: List of field names that must be present

    Returns:
        True if all fields are present

    Example:
        result = llm_strict(prompt)
        if not validate_json_fields(result, ["verdict", "explanation"]):
            raise Exception("LLM response missing required fields")
    """
    return all(field in result for field in required_fields)


def validate_enum_field(
    result: dict, field: str, allowed: list[str]
) -> bool:
    """
    Check that a field's value is one of the allowed values.

    Args:
        result: The parsed dict from exec_prompt
        field: The field name to check
        allowed: List of allowed values

    Returns:
        True if the field value is in the allowed list

    Example:
        result = llm_strict(prompt)
        if not validate_enum_field(result, "verdict", ["true", "false", "partially_true"]):
            raise Exception(f"Invalid verdict: {result.get('verdict')}")
    """
    return result.get(field) in allowed
