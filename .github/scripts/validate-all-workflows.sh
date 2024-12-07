#!/bin/bash
set -e

api_spec_dir="api-specs"

# OpenAPI Specification documents may be JSON or YAML
for spec in $(find $api_spec_dir -type f -name "*.json" -o -name "*.yaml" -o -name "*.yml"); do
  echo "Validating $spec"
  npx --yes mintlify openapi-check $spec
done
