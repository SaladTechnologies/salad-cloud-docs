#! /usr/bin/bash

api_spec_dir="api-specs"

# Spec can be in json or yaml
for spec in $(find $api_spec_dir -type f -name "*.json" -o -name "*.yaml" -o -name "*.yml"); do
  echo "Validating $spec"
  npx --yes @apidevtools/swagger-cli validate $spec
done
