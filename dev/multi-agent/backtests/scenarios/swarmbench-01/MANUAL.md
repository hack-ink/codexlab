# SwarmBench-01 Manual Replay

From repo root:

```sh
python3 dev/multi-agent/backtests/run_backtests.py
python3 dev/multi-agent/backtests/scenarios/swarmbench-01/verify_runtime.py
```

Optional fixture check:

```sh
cat dev/multi-agent/backtests/scenarios/swarmbench-01/dispatches.runtime.json
```

Expected:

- backtests pass with wait-any speedup and non-zero retry/dedup/lock-conflict metrics
- runtime verify passes, including a forced timebox-divergence rejection check
