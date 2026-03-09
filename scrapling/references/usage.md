# Scrapling Usage

## Install

```bash
export SCRAPLING_HOME="<installed skill root>"
export SCRAPLING_RUNTIME="$SCRAPLING_HOME/.runtime"
export SCRAPLING_VENV="$SCRAPLING_RUNTIME/venv"
export PLAYWRIGHT_BROWSERS_PATH="$SCRAPLING_RUNTIME/ms-playwright"

python3 -m venv "$SCRAPLING_VENV"
"$SCRAPLING_VENV/bin/python" -m pip install --upgrade pip
"$SCRAPLING_VENV/bin/python" -m pip install "scrapling[shell]"
```

All installers should use this private `venv` under the installed skill root. Do not install Scrapling into the source repo, the repo-wide shared `.venv`, or a global Python environment.

Use the smallest extra set that matches the task:

- `scrapling`
- `scrapling[shell]`
- `scrapling[fetchers]`
- `scrapling[ai]`
- `scrapling[all]`

When browser-backed fetchers are involved, install the matching extra set into the same `venv` and then run:

```bash
"$SCRAPLING_VENV/bin/scrapling" install
```

If you prefer not to activate the environment, define:

```bash
export SCRAPLING_BIN="$SCRAPLING_VENV/bin/scrapling"
export SCRAPLING_PY="$SCRAPLING_VENV/bin/python"
```

## CLI Fast Path

Static HTTP is the default escalation step after `curl` or simple fetch tools fail.

```bash
"$SCRAPLING_BIN" extract get 'https://example.com' output.md
"$SCRAPLING_BIN" extract get 'https://example.com' output.txt
"$SCRAPLING_BIN" extract get 'https://example.com' output.html
"$SCRAPLING_BIN" extract get 'https://example.com' article.md --css-selector '.article'
"$SCRAPLING_BIN" extract get 'https://example.com' article.md --css-selector '.article' --impersonate chrome
```

Use markdown or text output for LLM input. Use HTML only when the downstream task needs raw structure.

## Dynamic Browser Mode

Use this when the static HTML is missing the content you need.

```bash
"$SCRAPLING_BIN" extract fetch 'https://spa-site.com' content.md --no-headless
```

Switch here when the target page is a JavaScript shell, the data appears only after client rendering, or you need a browser wait strategy.

## Stealth Mode

Use this only for legitimate, authorized targets that present anti-bot or interstitial protection.

```bash
"$SCRAPLING_BIN" extract stealthy-fetch 'https://protected.com' content.html \
  --css-selector '#main' \
  --solve-cloudflare
```

Treat this as the last resort because it is heavier and higher-risk than static or normal browser fetches.

## Interactive Shell

Use the shell for quick experiments, selector tuning, and translating an existing `curl` request into Scrapling usage.

```bash
"$SCRAPLING_BIN" shell
```

The shell is useful when you want to try selectors interactively before committing to a script or agent workflow.

## Python Examples

Static one-off request:

```python
from scrapling.fetchers import Fetcher

page = Fetcher.get("https://quotes.toscrape.com/")
quotes = page.css(".quote .text::text").getall()
```

Static session with impersonation:

```python
from scrapling.fetchers import FetcherSession

with FetcherSession(impersonate="chrome") as session:
    page = session.get(
        "https://quotes.toscrape.com/",
        stealthy_headers=True,
    )
    quotes = page.css(".quote .text::text").getall()
```

Dynamic browser fetch:

```python
from scrapling.fetchers import DynamicFetcher

page = DynamicFetcher.fetch("https://quotes.toscrape.com/")
data = page.css(".quote .text::text").getall()
```

Dynamic session:

```python
from scrapling.fetchers import DynamicSession

with DynamicSession(headless=True, network_idle=True) as session:
    page = session.fetch("https://quotes.toscrape.com/", load_dom=False)
    data = page.xpath('//span[@class="text"]/text()').getall()
```

Stealth fetch:

```python
from scrapling.fetchers import StealthyFetcher

page = StealthyFetcher.fetch("https://nopecha.com/demo/cloudflare")
links = page.css("#padded_content a").getall()
```

API-style response handling:

```python
from scrapling.fetchers import Fetcher

page = Fetcher.get("https://api.github.com/events")
payload = page.json()
status = page.status
```

## Sessions And Async

- Use `FetcherSession` when you need cookie reuse or connection pooling.
- Use `DynamicSession` or `StealthySession` when repeated browser-backed fetches should share one browser context.
- Use async variants when scraping multiple URLs concurrently instead of looping serially.

## MCP

When the task is better served by reusable agent tools than ad hoc shell commands, install the AI extra and start the MCP server:

```bash
"$SCRAPLING_PY" -m pip install "scrapling[ai]"
"$SCRAPLING_BIN" mcp
```

The MCP server exposes tool-style operations for:

- `get`
- `bulk_get`
- `fetch`
- `bulk_fetch`
- `stealthy_fetch`
- `bulk_stealthy_fetch`

Prefer MCP for repeated agent-driven scraping loops. Prefer shell or Python for one-off extraction work.
