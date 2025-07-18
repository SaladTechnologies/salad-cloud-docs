#!/usr/bin/env python3
"""
Script to recursively remove empty groups and tabs from docs.json navigation.
This will clean up any empty navigation structures after reorganization.
"""

import json
import sys
from pathlib import Path


def remove_empty_navigation(navigation_data):
    """
    Recursively remove empty groups and tabs from navigation structure.

    Args:
        navigation_data: The navigation object from docs.json

    Returns:
        The cleaned navigation object
    """
    if not isinstance(navigation_data, dict) or 'tabs' not in navigation_data:
        return navigation_data

    cleaned_tabs = []

    for tab in navigation_data.get('tabs', []):
        if not isinstance(tab, dict):
            cleaned_tabs.append(tab)
            continue

        # Clean groups within this tab
        cleaned_groups = []

        for group in tab.get('groups', []):
            if not isinstance(group, dict):
                cleaned_groups.append(group)
                continue

            # Clean pages within this group
            cleaned_pages = clean_pages_recursively(group.get('pages', []))

            # Only keep the group if it has pages or is required for structure
            if cleaned_pages:
                group_copy = group.copy()
                group_copy['pages'] = cleaned_pages
                cleaned_groups.append(group_copy)

        # Only keep the tab if it has groups
        if cleaned_groups:
            tab_copy = tab.copy()
            tab_copy['groups'] = cleaned_groups
            cleaned_tabs.append(tab_copy)

    # Return updated navigation
    result = navigation_data.copy()
    result['tabs'] = cleaned_tabs
    return result


def clean_pages_recursively(pages):
    """
    Recursively clean pages list, removing empty nested groups.

    Args:
        pages: List of pages (can contain strings or nested group objects)

    Returns:
        Cleaned pages list
    """
    if not isinstance(pages, list):
        return pages

    cleaned_pages = []

    for page in pages:
        if isinstance(page, str):
            # Regular page reference, keep it
            cleaned_pages.append(page)
        elif isinstance(page, dict) and 'group' in page:
            # Nested group, clean it recursively
            nested_pages = clean_pages_recursively(page.get('pages', []))
            if nested_pages:
                page_copy = page.copy()
                page_copy['pages'] = nested_pages
                cleaned_pages.append(page_copy)
        else:
            # Other types, keep as-is
            cleaned_pages.append(page)

    return cleaned_pages


def main():
    """Main function to clean up docs.json navigation."""
    docs_json_path = Path(__file__).parent.parent / 'docs.json'

    if not docs_json_path.exists():
        print(f"Error: docs.json not found at {docs_json_path}")
        sys.exit(1)

    try:
        # Load current docs.json
        with open(docs_json_path, 'r', encoding='utf-8') as f:
            docs_data = json.load(f)

        print("Cleaning up navigation structure...")

        # Get original tab count
        original_tabs = len(docs_data.get('navigation', {}).get('tabs', []))

        # Clean the navigation
        if 'navigation' in docs_data:
            docs_data['navigation'] = remove_empty_navigation(
                docs_data['navigation'])

        # Get new tab count
        new_tabs = len(docs_data.get('navigation', {}).get('tabs', []))

        # Write the cleaned docs.json back
        with open(docs_json_path, 'w', encoding='utf-8') as f:
            json.dump(docs_data, f, indent=2, ensure_ascii=False)

        print(f"✅ Navigation cleanup complete!")
        print(f"   Tabs: {original_tabs} → {new_tabs}")

        if original_tabs > new_tabs:
            print(f"   Removed {original_tabs - new_tabs} empty tab(s)")

        # Show remaining tabs
        remaining_tabs = [tab.get('tab', 'Unnamed') for tab in docs_data.get(
            'navigation', {}).get('tabs', [])]
        if remaining_tabs:
            print(f"   Remaining tabs: {', '.join(remaining_tabs)}")

    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in docs.json: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
