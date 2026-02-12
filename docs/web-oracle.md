# Web Oracle Helpers

## The Problem

GenLayer contracts can access the internet natively, but fetching and parsing external data requires the same boilerplate every time: define an inner function, call `gl.nondet.web`, parse the response, wrap in `strict_eq`, deserialize.

For common data types like prices and scores, the prompt engineering is also repetitive.

## Functions

### `fetch_json_api(url, headers={})`

Fetch a JSON API endpoint with consensus. For REST APIs that return structured JSON.

```python
data = fetch_json_api("https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd")
btc_price = data["bitcoin"]["usd"]
```

With authentication:
```python
data = fetch_json_api(
    "https://api.example.com/data",
    headers={"Authorization": "Bearer your-key"}
)
```

### `fetch_and_extract(url, extraction_prompt, mode="text")`

Fetch a web page and use an LLM to extract specific data. For pages that don't have clean APIs.

```python
result = fetch_and_extract(
    url="https://weather.com/weather/today/l/new-york",
    extraction_prompt=(
        "Extract the current temperature.\\n"
        "{web_data}\\n"
        'Respond ONLY with JSON: {"temp": "<number>", "unit": "<F|C>"}'
    )
)
# result: {"temp": "72", "unit": "F"}
```

### `fetch_price(url, asset_name)`

Extract an asset price from any web source. Pre-built prompt for price extraction.

```python
result = fetch_price(
    url="https://www.coingecko.com/en/coins/bitcoin",
    asset_name="Bitcoin"
)
# result: {"price": "67500.42", "currency": "USD", "timestamp": "..."}
```

### `fetch_score(url, team1, team2)`

Extract a sports match score from any web source.

```python
result = fetch_score(
    url="https://www.espn.com/match/12345",
    team1="Arsenal",
    team2="Chelsea"
)
# result: {"score": "2:1", "winner": 1, "status": "finished"}
```

## Building Custom Extractors

Use `fetch_and_extract` as the base for any domain:

```python
def fetch_weather(url, city):
    prompt = f"""Extract weather data for {city}.
{{web_data}}
Respond ONLY with JSON: {{"temp": "<number>", "condition": "<sunny|cloudy|rainy|etc>", "humidity": "<percentage>"}}"""
    return fetch_and_extract(url, prompt)
```

## Example

See [price_feed.py](../examples/price_feed.py) for a complete oracle contract that stores and retrieves asset prices.
