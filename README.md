# context-engineering — Window Budget, Packing, Memory Summarization

> Open lab on **context engineering**: token budgets, deterministic message packing, and memory summarization — with offline unit tests (no API key).

**Author:** 马健文 / Evans Owen ([jianwen049-hub](https://github.com/jianwen049-hub))

| | |
|---|---|
| **Lab** | [`lab/`](./lab/) — packer + budget + memory + tests |
| **Blog** | [`docs/blog/`](./docs/blog/) |
| **Bio** | [`PROFILE.md`](./PROFILE.md) |

## Reading guide (EN)

```bash
cd lab
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export PYTHONPATH=src
python3 scripts/smoke_check.py
python3 -m context_lab.cli pack
python3 -m unittest discover -s tests -v
```

## License

MIT — see [`LICENSE`](./LICENSE).
