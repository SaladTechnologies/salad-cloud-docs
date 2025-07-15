#!/usr/bin/env python3
"""
Resolve redirect chains in docs.json

This script:
1. Reads redirect mappings from docs.json
2. Resolves all redirect chains so each source points directly to the final destination
3. Updates docs.json with the resolved redirects
4. Reports the changes made
"""

import json
import os
import sys
from typing import Dict, Set, List, Tuple


def load_docs_json(docs_json_path: str) -> dict:
    """Load the docs.json file"""
    with open(docs_json_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def build_redirect_map(redirects_array: List[dict]) -> Dict[str, str]:
    """Build a map of source -> destination from the redirects array"""
    redirect_map = {}
    for redirect in redirects_array:
        source = redirect.get('source', '').strip()
        destination = redirect.get('destination', '').strip()
        if source and destination:
            redirect_map[source] = destination
    return redirect_map


def resolve_redirect_chain(source: str, redirect_map: Dict[str, str], max_depth: int = 20) -> Tuple[str, List[str]]:
    """
    Resolve a redirect chain to find the final destination
    Returns (final_destination, chain_path)
    """
    chain = [source]
    current = source
    visited = set()
    depth = 0

    while current in redirect_map and depth < max_depth:
        if current in visited:
            # Circular redirect detected
            print(
                f"⚠️  Warning: Circular redirect detected in chain: {' -> '.join(chain)}")
            break

        visited.add(current)
        next_dest = redirect_map[current]
        chain.append(next_dest)
        current = next_dest
        depth += 1

    if depth >= max_depth:
        print(
            f"⚠️  Warning: Max redirect depth ({max_depth}) reached for source: {source}")

    final_destination = chain[-1]
    return final_destination, chain


def resolve_all_redirects(docs_json_path: str, dry_run: bool = False) -> Tuple[int, int, int]:
    """
    Resolve all redirect chains in docs.json
    Returns (total_redirects, chains_resolved, changes_made)
    """
    print(f"📖 Loading docs.json from {docs_json_path}")
    docs = load_docs_json(docs_json_path)

    redirects_array = docs.get('redirects', [])
    redirect_map = build_redirect_map(redirects_array)

    print(f"🔍 Found {len(redirects_array)} redirects in docs.json")
    print(f"🗺️  Built redirect map with {len(redirect_map)} entries")

    # Track statistics
    total_redirects = len(redirects_array)
    chains_resolved = 0
    changes_made = 0

    # Resolve each redirect
    for i, redirect in enumerate(redirects_array):
        source = redirect.get('source', '').strip()
        destination = redirect.get('destination', '').strip()

        if not source or not destination:
            continue

        # Resolve the chain starting from this destination
        final_destination, chain = resolve_redirect_chain(
            destination, redirect_map)

        # If the chain has more than one hop, we need to update
        if len(chain) > 1:
            chains_resolved += 1

            # Check if we actually need to change the destination
            if final_destination != destination:
                changes_made += 1

                print(f"🔗 Chain {chains_resolved}: {source}")
                print(f"   Original: {destination}")
                print(f"   Resolved: {final_destination}")
                print(f"   Full chain: {' -> '.join(chain)}")
                print()

                # Update the redirect if not in dry run mode
                if not dry_run:
                    redirects_array[i]['destination'] = final_destination

    # Save the updated docs.json if not in dry run mode and changes were made
    if not dry_run and changes_made > 0:
        print(
            f"💾 Saving updated docs.json with {changes_made} resolved redirects...")
        with open(docs_json_path, 'w', encoding='utf-8') as f:
            json.dump(docs, f, indent=2, ensure_ascii=False)
        print(f"✅ Successfully updated {docs_json_path}")

    return total_redirects, chains_resolved, changes_made


def validate_redirects(docs_json_path: str) -> bool:
    """
    Validate that there are no redirect chains remaining
    Returns True if all redirects are direct (no chains)
    """
    print("🔍 Validating redirect chains...")
    docs = load_docs_json(docs_json_path)
    redirects_array = docs.get('redirects', [])
    redirect_map = build_redirect_map(redirects_array)

    chains_found = 0

    for redirect in redirects_array:
        source = redirect.get('source', '').strip()
        destination = redirect.get('destination', '').strip()

        if not source or not destination:
            continue

        # Check if destination has another redirect
        if destination in redirect_map:
            chains_found += 1
            final_destination, chain = resolve_redirect_chain(
                destination, redirect_map)
            print(f"⚠️  Chain still exists: {source} -> {' -> '.join(chain)}")

    if chains_found == 0:
        print("✅ No redirect chains found - all redirects are direct!")
        return True
    else:
        print(
            f"❌ Found {chains_found} redirect chains that still need resolution")
        return False


def main():
    """Main function"""
    if len(sys.argv) < 2:
        print(
            "Usage: python resolve-redirect-chains.py <docs.json> [--dry-run] [--validate]")
        print()
        print("Options:")
        print("  --dry-run    Show what would be changed without making changes")
        print("  --validate   Validate that no chains exist (run after resolution)")
        sys.exit(1)

    docs_json_path = sys.argv[1]
    dry_run = '--dry-run' in sys.argv
    validate_only = '--validate' in sys.argv

    if not os.path.exists(docs_json_path):
        print(f"❌ Error: {docs_json_path} not found")
        sys.exit(1)

    if validate_only:
        success = validate_redirects(docs_json_path)
        sys.exit(0 if success else 1)

    print("🚀 Starting redirect chain resolution...")
    print(f"📄 Target file: {docs_json_path}")
    print(f"🧪 Dry run mode: {'ON' if dry_run else 'OFF'}")
    print()

    try:
        total_redirects, chains_resolved, changes_made = resolve_all_redirects(
            docs_json_path, dry_run)

        print("📊 Summary:")
        print(f"  Total redirects processed: {total_redirects}")
        print(f"  Redirect chains found: {chains_resolved}")
        print(f"  Changes made: {changes_made}")

        if dry_run and changes_made > 0:
            print()
            print("🧪 This was a dry run. Run without --dry-run to apply changes.")
        elif changes_made > 0:
            print()
            print("✅ Redirect chains have been resolved!")
            print("🔍 Run with --validate to confirm no chains remain.")
        else:
            print()
            print("✨ No redirect chains found - all redirects are already direct!")

    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
