---
name: scrapling
description: Browser-backed fallback scraping with Scrapling for pages that lightweight system-level fetches cannot retrieve. Use when system `curl`, built-in web fetch, or web search is blocked, interstitialed, or stripped by JavaScript or anti-bot protection, then escalate with Scrapling dynamic or stealth fetchers.
---

# Scrapling

## Overview

Use Scrapling as the escalation path only after the lightest system-level retrieval path has already failed. Start with system `curl`, built-in web fetch, or direct docs access first. If those paths are blocked, interstitialed, or stripped by JavaScript, use Scrapling's browser-backed fetchers. Reserve stealth mode for bot-protected targets the user is authorized to access.

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
- Browser-backed fallback fetching: `scrapling[fetchers]`
- Interactive shell on top of fetchers: `scrapling[shell]`
- MCP server support on top of fetchers: `scrapling[ai]`
- Everything: `scrapling[all]`

For the default fallback workflow in this skill, prefer `scrapling[fetchers]`. Add `shell` only when you need interactive probing, and add `ai` only when you actually need the MCP server. Avoid `scrapling[all]` unless you explicitly need every mode, because it pulls in extra tooling that the normal fallback path does not use.

## Mode Ladder

1. Start with system-level `curl` or an equivalent lightweight fetch outside Scrapling.
If that path succeeds, keep using it. Do not invoke Scrapling just to replace a working lightweight fetch.

2. Escalate to dynamic browser mode via `scrapling extract fetch` or `DynamicFetcher.fetch`.
Use this when `curl` or built-in fetches cannot retrieve the target content because the page is a JavaScript shell, an interstitial blocks the response, or the returned HTML is not the real page.

3. Escalate to stealth mode via `scrapling extract stealthy-fetch` or `StealthyFetcher.fetch`.
Use this only for explicit anti-bot or interstitial cases such as Cloudflare-style blocking, and only when the user is authorized to access the target.

4. Use sessions or async variants when state or scale matters.
Reach for `DynamicSession`, `StealthySession`, or async equivalents when you need cookie reuse, pooled browser tabs, or multiple URLs.

5. Use MCP when the task needs reusable scraping tools instead of one-off commands.
This is the right path for agent loops that need repeated browser-backed or stealth fetch operations without shelling out each time.

## Extraction Rules

- Prefer selector-targeted extraction over full-page dumps.
- Prefer markdown or text for LLM consumption unless the task explicitly needs raw HTML.
- Use `page.css(...)`, `page.xpath(...)`, and `page.json()` instead of ad hoc string slicing.
- Keep system `curl` or an equivalent lightweight fetch as the default first step.
- Use Scrapling only when those lightweight paths are blocked or cannot expose the real content.
- Treat stealth mode as the expensive last resort.

## Failure Recovery

- If system `curl` or a built-in fetch succeeds, stay on that lightweight path and extract locally.
- If you only see placeholders, loading shells, interstitials, or anti-bot refusals, switch to dynamic mode.
- If the browser path still gets blocked by anti-bot checks, escalate to stealth mode only when the target and access are legitimate.
- If you need to inspect or tune selectors after switching to Scrapling, use `scrapling shell` for quick manual probing.

## Safety Constraints

- Respect robots.txt, site terms, and user authorization boundaries.
- Do not use stealth mode to bypass login, paywall, or access controls the user is not entitled to use.
- Keep cookies, tokens, and proxy credentials out of logs and durable artifacts.

## References

- Read [references/usage.md](references/usage.md) for the required `venv` bootstrap plus copy-paste CLI and Python examples.
- Load the reference file only when you need concrete command patterns or MCP/session examples.
