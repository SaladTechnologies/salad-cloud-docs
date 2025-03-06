#!/bin/bash

# Check if we're in a git repository
if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "Error: Not in a git repository." >&2
  exit 1
fi

# Get the root directory of the git repository
GIT_ROOT=$(git rev-parse --show-toplevel)

# Start building the JSON file
echo "{" >all-updates.json

# Flag to track if this is the first entry (for comma handling)
FIRST_ENTRY=true

# Find all mdx files recursively and process them
find . -type f -name "*.mdx" | sort | while read -r file; do
  # Get the last modification date of the file from git
  # Extract just the date portion in YYYY-MM-DD format
  LAST_UPDATE=$(git log -1 --format="%as" -- "$file" 2>/dev/null)

  # If git has no history for this file, it might be new and uncommitted
  if [ -z "$LAST_UPDATE" ]; then
    # Use file system modification time as fallback (date only)
    LAST_UPDATE=$(date -r "$file" +"%Y-%m-%d")
  fi

  # Get relative path from the git root
  RELATIVE_PATH="${file#./}"

  # Add comma for all entries except the first one
  if [ "$FIRST_ENTRY" = true ]; then
    FIRST_ENTRY=false
  else
    echo "," >>all-updates.json
  fi

  # Write the entry to the JSON file
  # Proper JSON escaping for the filepath
  ESCAPED_PATH=$(echo "$RELATIVE_PATH" | sed 's/\\/\\\\/g; s/"/\\"/g')
  echo "  \"$ESCAPED_PATH\": \"$LAST_UPDATE\"" >>all-updates.json
done

# Close the JSON object
echo "}" >>all-updates.json

# Use jq to format the file
jq . all-updates.json >all-updates.json.tmp
mv all-updates.json.tmp all-updates.json

echo "JSON file 'all-updates.json' created successfully!"
