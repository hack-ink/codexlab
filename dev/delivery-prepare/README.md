# delivery-prepare (Dev-only)

This directory contains repo-local smoke coverage for the `delivery-prepare` skill. It
stays outside the installable skill directory so the installed skill only ships its runtime
contract and helper scripts.

## Quick smoke

From the repo root:

```sh
python3 dev/delivery-prepare/run_smoke.py
```

The smoke validates:

- `build_delivery_contract.py` allows untracked delivery contracts with empty refs
- `build_delivery_contract.py` rejects `--linear-ref` without `--authority-linear-ref`
- `build_delivery_contract.py` fails when `--delivery-mode` is missing
- `build_delivery_contract.py` emits `delivery/1` typed refs
- `validate_delivery_contract.py` accepts empty or GitHub-only refs while rejecting invalid authority, mode, related-only Linear refs, and bad ref shapes
- `validate_delivery_contract.py` accepts valid `delivery/1` contracts
