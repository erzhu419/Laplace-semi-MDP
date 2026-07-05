#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

lean proof/RDOperator.lean
(cd proof && lake env lean RDOperatorReal.lean)
