#!/bin/bash

# Check if jq is installed
if ! command -v jq &>/dev/null; then
  echo "Error: jq is required but not installed." >&2
  exit 1
fi

# Check if the JSON file exists
if [ ! -f "all-updates.json" ]; then
  echo "Error: all-updates.json file not found." >&2
  exit 1
fi

# For each file in the JSON
jq -r 'keys[]' all-updates.json | while read -r file; do
  # Skip if file doesn't exist (might have been deleted)
  if [ ! -f "$file" ]; then
    echo "Warning: File $file not found, skipping." >&2
    continue
  fi

  # Get the last update date for this file
  update_date=$(jq -r --arg file "$file" '.[$file]' all-updates.json)

  echo "Processing $file (Last Updated: $update_date)"

  # Create a temporary file
  temp_file=$(mktemp)

  # Process the file to add the Last Updated line after YAML frontmatter
  awk -v date="$update_date" '
    BEGIN { in_frontmatter = 0; added = 0; }
    /^---$/ {
      print $0;
      if (in_frontmatter) {
        in_frontmatter = 0;
        print "";
        print "*Last Updated: " date "*";
        print "";
        added = 1;
      } else {
        in_frontmatter = 1;
      }
      next;
    }
    { print $0; }
    END {
      # If no frontmatter was found, add at the beginning
      if (!added) {
        print "*Last Updated: " date "*" > "/tmp/header";
        print "" > "/tmp/header";
        system("cat /tmp/header " FILENAME " > /tmp/combined && mv /tmp/combined " FILENAME);
      }
    }
  ' "$file" >"$temp_file"

  # Replace the original file with the temporary file
  mv "$temp_file" "$file"
done

echo "All MDX files have been updated with 'Last Updated' information."
