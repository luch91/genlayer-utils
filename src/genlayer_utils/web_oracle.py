# genlayer-utils: web_oracle.py
# Web data extraction helpers with built-in consensus for GenLayer Intelligent Contracts
#
# Domain-specific functions for fetching and parsing external data sources.
# Each function wraps the full non-deterministic block pattern so you don't
# have to write it yourself. Copy the functions you need into your contract file.
#
# Requires: from genlayer import *
#           import json

import json
from genlayer import *


def fetch_json_api(url: str, *, headers: dict = {}) -> dict:
    """
    Fetch a JSON API endpoint with strict equality consensus.
    Handles the full non-deterministic block pattern for REST API calls.

    Args:
        url: API endpoint URL
        headers: Optional HTTP headers (e.g., for API keys)

    Returns:
        Parsed dict from the API response

    Example:
        data = fetch_json_api("https://api.example.com/data")
        price = data["price"]
    """
    def _inner() -> str:
        resp = gl.nondet.web.get(url, headers=headers)
        if resp.status != 200:
            raise Exception(f"API returned status {resp.status}")
        data = json.loads(resp.body)
        return json.dumps(data, sort_keys=True)

    return json.loads(gl.eq_principle.strict_eq(_inner))


def fetch_and_extract(
    url: str,
    extraction_prompt: str,
    *,
    mode: str = "text",
) -> dict:
    """
    Fetch a web page and use an LLM to extract specific data from it.
    Combines web scraping + AI extraction + consensus in one call.

    Args:
        url: Web page URL
        extraction_prompt: Prompt with {web_data} placeholder describing
                           what to extract and the expected JSON format
        mode: "text", "html", or "screenshot"

    Returns:
        Parsed dict with extracted data

    Example:
        result = fetch_and_extract(
            url="https://weather.example.com/new-york",
            extraction_prompt=(
                "Extract the current temperature from this page.\\n"
                "{web_data}\\n"
                "Respond ONLY with JSON: {{\"temp\": \"<number>\", \"unit\": \"<F|C>\"}}"
            )
        )
    """
    def _inner() -> str:
        web_data = gl.nondet.web.render(url, mode=mode)
        prompt = extraction_prompt.format(web_data=web_data)
        result = gl.nondet.exec_prompt(prompt, response_format="json")
        if isinstance(result, dict):
            return json.dumps(result, sort_keys=True)
        return result

    return json.loads(gl.eq_principle.strict_eq(_inner))


def fetch_price(url: str, asset_name: str) -> dict:
    """
    Fetch and extract an asset price from a web source.
    Returns a dict with price, currency, and timestamp.

    Args:
        url: Web page or API URL containing the price
        asset_name: Name of the asset (e.g., "Bitcoin", "Gold", "AAPL")

    Returns:
        {"price": str, "currency": str, "timestamp": str}

    Example:
        result = fetch_price(
            url="https://www.coingecko.com/en/coins/bitcoin",
            asset_name="Bitcoin"
        )
        # result: {"price": "67500.42", "currency": "USD", "timestamp": "..."}
    """
    prompt = f"""Extract the current price of {asset_name} from this web page.

WEB CONTENT:
{{web_data}}

Respond ONLY with this exact JSON format, nothing else:
{{{{"price": "<numeric value as string>", "currency": "<USD|EUR|GBP|etc>", "timestamp": "<if available, otherwise unknown>"}}}}

Rules:
- Extract only the most recent/current price
- Use the primary currency shown on the page
- Your response must be valid JSON only, no extra text"""

    return fetch_and_extract(url, prompt)


def fetch_score(url: str, team1: str, team2: str) -> dict:
    """
    Fetch and extract a sports match score from a web source.

    Args:
        url: Web page URL with match results
        team1: Name of the first team
        team2: Name of the second team

    Returns:
        {"score": str, "winner": int, "status": str}
        winner: 0=draw, 1=team1, 2=team2, -1=not played

    Example:
        result = fetch_score(
            url="https://www.espn.com/match/12345",
            team1="Arsenal",
            team2="Chelsea"
        )
        # result: {"score": "2:1", "winner": 1, "status": "finished"}
    """
    prompt = f"""Extract the match result for {team1} vs {team2}.

WEB CONTENT:
{{web_data}}

Respond ONLY with this exact JSON format, nothing else:
{{{{"score": "<e.g. 2:1, or - if not played>", "winner": <0 for draw, 1 for {team1}, 2 for {team2}, -1 if not played>, "status": "<finished|in_progress|not_started>"}}}}

Rules:
- Use -1 for winner if the match hasn't been played yet
- Your response must be valid JSON only, no extra text"""

    return fetch_and_extract(url, prompt)
