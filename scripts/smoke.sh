#!/usr/bin/env bash
# Run all real ARGoS experiments and check their collective behavior.
set -euo pipefail
cd "$(dirname "$0")/.."
exec "${PYTHON:-python}" -m pytest -q -m argos tests/test_experiments.py
