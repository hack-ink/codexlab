---
name: scrapling
description: Adaptive web scraping with Scrapling for pages that break simple fetch tools. Use when Codex needs to extract content from static pages, JavaScript-rendered pages, or bot-protected pages via Scrapling CLI, Python, or MCP, especially after `curl`, built-in web fetch, or web search tools return incomplete, blocked, or low-fidelity results.
---

# Scrapling

## Overview

Use Scrapling as the escalation path when `curl`, built-in web fetch, or search tools cannot return the page fidelity you need. Start with fast HTTP scraping, escalate to a real browser for JavaScript pages, and reserve stealth mode for bot-protected targets the user is authorized to access.

All Scrapling installs for this skill must live in a private `venv` under the installed skill root. Do not install Scrapling into the source repo, the repo-wide shared `.venv`, or a global Python environment.

## Inputs

- Target URL or URL set
- Desired output shape: markdown, text, HTML, or structured selector results
- Optional CSS selector or XPath target
- Signals that JavaScript rendering, cookies, or anti-bot handling may be required
- Whether the task is one-off shell usage, reusable Python code, or MCP exposure for an agent loop

## Runtime Isolation

- First resolve the installed Scrapling skill root from the runtime skills list and treat it as `$SCRAPLING_HOME`.
- Create and reuse a private runtime under `$SCRAPLING_HOME/.runtime/`.
- The Python environment must be `$SCRAPLING_HOME/.runtime/venv`.
- Browser state for `scrapling install` should live under `$SCRAPLING_HOME/.runtime/` as well, for example `PLAYWRIGHT_BROWSERS_PATH="$SCRAPLING_HOME/.runtime/ms-playwright"`.
- Remove or reinstall the installed skill directory to remove or rebuild its runtime.

## Install Gate

1. Create the private runtime with `python3 -m venv "$SCRAPLING_HOME/.runtime/venv"`.
2. Install the smallest Scrapling extra set that matches the task into that `venv`.
3. Run all Scrapling CLI commands from that `venv`, either by activation or by calling the binary under `$SCRAPLING_HOME/.runtime/venv/bin/`.
4. If dynamic or stealth fetchers are in scope, run `scrapling install` inside that `venv` and keep its browser artifacts under `$SCRAPLING_HOME/.runtime/`.

Use these extra sets:

- Parser only: `scrapling`
- CLI and interactive shell: `scrapling[shell]`
- Dynamic and stealth fetchers: `scrapling[fetchers]`
- MCP server support: `scrapling[ai]`
- Everything: `scrapling[all]`

## Mode Ladder

1. Start with static HTTP via `scrapling extract get` or `Fetcher.get`.
Use this for normal HTML pages, JSON endpoints, and cases where `curl` only needs better impersonation or selector-targeted extraction.

2. Escalate to dynamic browser mode via `scrapling extract fetch` or `DynamicFetcher.fetch`.
Use this when the initial HTML is missing the target content, the page is a JavaScript shell, or you need browser rendering and wait strategies.

3. Escalate to stealth mode via `scrapling extract stealthy-fetch` or `StealthyFetcher.fetch`.
Use this only for explicit anti-bot or interstitial cases such as Cloudflare-style blocking, and only when the user is authorized to access the target.

4. Use sessions or async variants when state or scale matters.
Reach for `FetcherSession`, `DynamicSession`, `StealthySession`, or async equivalents when you need cookie reuse, pooled browser tabs, or multiple URLs.

5. Use MCP when the task needs reusable scraping tools instead of one-off commands.
This is the right path for agent loops that need repeated `get`, `fetch`, or stealth fetch operations without shelling out each time.

## Extraction Rules

- Prefer selector-targeted extraction over full-page dumps.
- Prefer markdown or text for LLM consumption unless the task explicitly needs raw HTML.
- Use `page.css(...)`, `page.xpath(...)`, and `page.json()` instead of ad hoc string slicing.
- Keep browser mode as a second step, not the default.
- Treat stealth mode as the expensive last resort.

## Failure Recovery

- If `curl` or a built-in fetch returns partial HTML, retry in static Scrapling mode with impersonation and a selector.
- If you only see placeholders, loading shells, or empty containers, switch to dynamic mode.
- If the browser path still gets blocked by anti-bot checks, escalate to stealth mode only when the target and access are legitimate.
- If you need to inspect or translate an existing `curl` flow, use `scrapling shell` for quick manual probing.

## Safety Constraints

- Respect robots.txt, site terms, and user authorization boundaries.
- Do not use stealth mode to bypass login, paywall, or access controls the user is not entitled to use.
- Keep cookies, tokens, and proxy credentials out of logs and durable artifacts.

## References

- Read [references/usage.md](references/usage.md) for the required `venv` bootstrap plus copy-paste CLI and Python examples.
- Load the reference file only when you need concrete command patterns or MCP/session examples.
