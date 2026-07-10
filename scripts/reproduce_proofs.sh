#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

lean proof/RDOperator.lean
lean proof/AdaptiveTopK.lean
(cd proof && lake env lean RDOperatorReal.lean)
(cd proof && lake env lean OneShotRDOperator.lean)
