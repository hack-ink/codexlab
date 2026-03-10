# Scrapling Usage

## Install

```bash
export SCRAPLING_HOME="<installed skill root>"
export SCRAPLING_RUNTIME="$SCRAPLING_HOME/.runtime"
export SCRAPLING_VENV="$SCRAPLING_RUNTIME/venv"
export PLAYWRIGHT_BROWSERS_PATH="$SCRAPLING_RUNTIME/ms-playwright"

python3 -m venv "$SCRAPLING_VENV"
"$SCRAPLING_VENV/bin/python" -m pip install --upgrade pip
"$SCRAPLING_VENV/bin/python" -m pip install "scrapling[fetchers]"
```

All installers should use this private `venv` under the installed skill root. Do not install Scrapling into the source repo, the repo-wide shared `.venv`, or a global Python environment.

Use the smallest extra set that matches the task:

- `scrapling`
- `scrapling[fetchers]`
- `scrapling[shell]`
- `scrapling[ai]`
- `scrapling[all]`

For the default "system `curl` first, Scrapling only when blocked" workflow, `scrapling[fetchers]` is enough. Add `scrapling[shell]` only if you need `scrapling shell`. Add `scrapling[ai]` only if you need `scrapling mcp`. Avoid `scrapling[all]` unless you knowingly want both optional layers.

When browser-backed fetchers are involved, install the matching extra set into the same `venv` and then run:

```bash
"$SCRAPLING_VENV/bin/scrapling" install
```

If you prefer not to activate the environment, define:

```bash
export SCRAPLING_BIN="$SCRAPLING_VENV/bin/scrapling"
export SCRAPLING_PY="$SCRAPLING_VENV/bin/python"
```

## Retrieval Policy

Default to the lightest and fastest viable path outside Scrapling first:

- system `curl`
- built-in web fetch tools
- direct docs access

If one of those paths succeeds, keep using it. Do not invoke Scrapling just to replace a working lightweight fetch.

## Dynamic Browser Mode

Use this when system `curl` or a built-in fetch cannot retrieve the real page content.

```bash
"$SCRAPLING_BIN" extract fetch 'https://spa-site.com' content.md --no-headless
```

Switch here when the target page is a JavaScript shell, an interstitial blocks the response, Cloudflare or a similar anti-bot layer rejects lightweight requests, or the returned HTML is not the real rendered page.

## Stealth Mode

Use this only for legitimate, authorized targets that present anti-bot or interstitial protection.

```bash
"$SCRAPLING_BIN" extract stealthy-fetch 'https://protected.com' content.html \
  --css-selector '#main' \
  --solve-cloudflare
```

Treat this as the last resort because it is heavier and higher-risk than normal browser fetches.

## Interactive Shell

Use the shell for quick experiments and selector tuning after you have already decided a browser-backed Scrapling path is necessary.

```bash
"$SCRAPLING_BIN" shell
```

The shell is useful when you want to try selectors interactively before committing to a script or agent workflow.

## Python Examples

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

## Sessions And Async

- Use `DynamicSession` or `StealthySession` when repeated browser-backed fetches should share one browser context.
- Use async variants when scraping multiple URLs concurrently instead of looping serially.

## MCP

When the task is better served by reusable agent tools than ad hoc shell commands, install the AI extra and start the MCP server:

```bash
"$SCRAPLING_PY" -m pip install "scrapling[ai]"
"$SCRAPLING_BIN" mcp
```

The MCP server exposes tool-style operations for browser-backed and stealth fetch workflows.

Prefer MCP for repeated agent-driven scraping loops. Prefer shell or Python for one-off extraction work after lightweight system fetches have already failed.
