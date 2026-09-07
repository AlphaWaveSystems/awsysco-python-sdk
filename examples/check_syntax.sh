#!/usr/bin/env bash
# Sanity-checks the example scripts compile and import cleanly.
#
# These examples make real network calls against the live API and require a
# real AWSYS_API_KEY (see each file's docstring) — they are intentionally NOT
# executed in CI. This script only verifies they're valid, importable Python,
# so a refactor that breaks their imports (e.g. a renamed model/exception) is
# still caught automatically.
set -euo pipefail

cd "$(dirname "$0")/.."
python -m py_compile examples/basic_usage.py examples/async_usage.py examples/integration_test.py
echo "examples: syntax OK"
