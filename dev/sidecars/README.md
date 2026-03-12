# sidecars maintainer checks

This dev directory validates the hard-cut source surface for `sidecars`.

Run:

```bash
python3 dev/sidecars/run_smoke.py
```

The smoke test checks that:

- the new `sidecars` skill exists
- the deleted `multi-agent` source surface is gone
- repo docs point to `sidecars`

Runtime source validation lives separately under:

```bash
python3 home/codex/bin/run_sidecars_source_smoke.py
```

Run that command from the nix repo that owns the `home/codex/` source tree.
