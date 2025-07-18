#!/usr/bin/env python3
"""
Script to clean up duplicate redirects in docs.json, keeping only the most recent redirect for each source.
This ensures that the last/most recently added redirect takes precedence over older ones.
"""

import json
import sys
from pathlib import Path
from collections import OrderedDict


def find_duplicate_sources(redirects):
    """
    Find all duplicate source entries in the redirects array.

    Args:
        redirects: List of redirect objects with 'source' and 'destination' keys

    Returns:
        dict: Source -> list of indices where that source appears
    """
    source_indices = {}

    for i, redirect in enumerate(redirects):
        if not isinstance(redirect, dict) or 'source' not in redirect:
            continue

        source = redirect['source']
        if source not in source_indices:
            source_indices[source] = []
        source_indices[source].append(i)

    # Only return sources that appear more than once
    return {source: indices for source, indices in source_indices.items() if len(indices) > 1}


def remove_duplicate_redirects(redirects):
    """
    Remove duplicate redirect sources, keeping only the last occurrence of each source.

    Args:
        redirects: List of redirect objects

    Returns:
        tuple: (cleaned_redirects, duplicates_info)
    """
    duplicates = find_duplicate_sources(redirects)

    if not duplicates:
        return redirects, {}

    # Track which indices to remove (all but the last occurrence of each duplicate)
    indices_to_remove = set()
    duplicates_info = {}

    for source, indices in duplicates.items():
        # Keep the last occurrence, remove all others
        indices_to_keep = indices[-1]  # Last index
        indices_to_remove.update(indices[:-1])  # All but last

        duplicates_info[source] = {
            'total_occurrences': len(indices),
            'kept_index': indices_to_keep,
            'removed_indices': indices[:-1],
            'kept_destination': redirects[indices_to_keep]['destination'],
            'removed_destinations': [redirects[i]['destination'] for i in indices[:-1]]
        }

    # Create new redirects list without duplicates
    cleaned_redirects = [
        redirect for i, redirect in enumerate(redirects)
        if i not in indices_to_remove
    ]

    return cleaned_redirects, duplicates_info


def main():
    """Main function to clean up duplicate redirects in docs.json."""
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

        original_count = len(docs_data['redirects'])
        print(f"Found {original_count} redirects in docs.json")

        # Find and display duplicates before cleaning
        duplicates = find_duplicate_sources(docs_data['redirects'])

        if not duplicates:
            print("✅ No duplicate redirect sources found!")
            return

        print(f"\n🔍 Found {len(duplicates)} sources with duplicate redirects:")
        for source, indices in duplicates.items():
            print(
                f"  '{source}' appears {len(indices)} times at indices {indices}")

        # Clean up duplicates
        cleaned_redirects, duplicates_info = remove_duplicate_redirects(
            docs_data['redirects'])

        # Update docs.json
        docs_data['redirects'] = cleaned_redirects
        new_count = len(cleaned_redirects)

        # Write the cleaned docs.json back
        with open(docs_json_path, 'w', encoding='utf-8') as f:
            json.dump(docs_data, f, indent=2, ensure_ascii=False)

        print(f"\n✅ Redirect cleanup complete!")
        print(f"   Original redirects: {original_count}")
        print(f"   Cleaned redirects: {new_count}")
        print(f"   Removed duplicates: {original_count - new_count}")

        # Show detailed information about what was cleaned
        print(f"\n📋 Cleanup Details:")
        for source, info in duplicates_info.items():
            print(f"   Source: '{source}'")
            print(f"     → Kept destination: '{info['kept_destination']}'")
            if info['removed_destinations']:
                removed_dests = "', '".join(info['removed_destinations'])
                print(f"     → Removed destinations: '{removed_dests}'")
            print()

    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in docs.json: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
