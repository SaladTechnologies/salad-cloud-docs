#!/usr/bin/env python3
"""
Test script to demonstrate the redirect cleanup functionality by adding some test duplicates
and then running the cleanup.
"""

import json
import sys
from pathlib import Path


def main():
    """Add test duplicates to docs.json to demonstrate cleanup functionality."""
    docs_json_path = Path(__file__).parent.parent / 'docs.json'

    if not docs_json_path.exists():
        print(f"Error: docs.json not found at {docs_json_path}")
        sys.exit(1)

    try:
        # Load current docs.json
        with open(docs_json_path, 'r', encoding='utf-8') as f:
            docs_data = json.load(f)

        if 'redirects' not in docs_data:
            print("No redirects found in docs.json")
            return

        # Add some test duplicate redirects to demonstrate cleanup
        test_redirects = [
            {
                "source": "/test-duplicate-1",
                "destination": "/old-destination-1"
            },
            {
                "source": "/test-duplicate-2",
                "destination": "/old-destination-2"
            },
            {
                "source": "/test-duplicate-1",  # Duplicate of first
                "destination": "/newer-destination-1"
            },
            {
                "source": "/test-duplicate-1",  # Another duplicate - this should be kept
                "destination": "/newest-destination-1"
            },
            {
                "source": "/test-duplicate-2",  # Duplicate of second - this should be kept
                "destination": "/newer-destination-2"
            }
        ]

        original_count = len(docs_data['redirects'])
        docs_data['redirects'].extend(test_redirects)
        new_count = len(docs_data['redirects'])

        # Write back with test duplicates
        with open(docs_json_path, 'w', encoding='utf-8') as f:
            json.dump(docs_data, f, indent=2, ensure_ascii=False)

        print(
            f"✅ Added {len(test_redirects)} test redirects ({new_count - original_count} new entries)")
        print(f"   Including 3 duplicates for '/test-duplicate-1' and 2 for '/test-duplicate-2'")
        print(f"   Total redirects: {original_count} → {new_count}")
        print("\nNow run: python scripts/cleanup-redirects.py")

    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in docs.json: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
