#!/usr/bin/env bash
# Fail fast: without this, a failure in cyclonedx-py surfaces further down as a
# confusing "could not find cyclonedx-sbom.json" from the convert step.
set -euo pipefail

cyclonedx-py --e --format json -o cyclonedx-sbom.json
wget https://github.com/CycloneDX/cyclonedx-cli/releases/download/v0.24.2/cyclonedx-linux-x64
chmod u+x cyclonedx-linux-x64
./cyclonedx-linux-x64 convert --input-format json --output-format spdxjson --input-file cyclonedx-sbom.json --output-file spdx.json
