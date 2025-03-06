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
  # Extract the date and format it as "Month Day, Year"
  if git log -1 --format="%at" -- "$file" >/dev/null 2>&1; then
    # Get Unix timestamp and convert to long-form date
    TIMESTAMP=$(git log -1 --format="%at" -- "$file")
    LAST_UPDATE=$(date -d @"$TIMESTAMP" +"%B %d, %Y")
  else
    # Use file system modification time as fallback
    LAST_UPDATE=$(date -r "$file" +"%B %d, %Y")
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

  if grep -q "\*Last Updated:" "$file"; then
    # Update the existing "Last Updated" line
    sed -i "s|\*Last Updated:.*\*|\*Last Updated: $update_date\*|" "$file"
    echo "  Updated existing 'Last Updated' line"
  else
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
    echo "  Added new 'Last Updated' line"
  fi
done

echo "All MDX files have been updated with 'Last Updated' information."

# Clean up the temporary JSON file
rm all-updates.json
