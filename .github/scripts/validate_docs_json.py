#!/usr/bin/env python3
"""
Script to validate that all pages in docs.json have corresponding .mdx files
and all .mdx files have corresponding entries in docs.json.
"""

import json
import os
import sys
from pathlib import Path
from typing import Set, List, Dict, Tuple

def extract_pages_from_json(data: dict, base_path: str = "") -> Set[str]:
    """
    Recursively extract all page references from the docs.json structure.
    Returns a set of page paths (without .mdx extension).
    """
    pages = set()
    
    def extract_recursive(obj, current_path=""):
        if isinstance(obj, dict):
            # Check for 'pages' key
            if 'pages' in obj:
                for page in obj['pages']:
                    if isinstance(page, str):
                        pages.add(page)
                    elif isinstance(page, dict):
                        extract_recursive(page, current_path)
            
            # Check for 'groups' key in navigation
            if 'groups' in obj:
                for group in obj['groups']:
                    extract_recursive(group, current_path)
            
            # Check for 'tabs' in navigation
            if 'tabs' in obj and isinstance(obj['tabs'], list):
                for tab in obj['tabs']:
                    extract_recursive(tab, current_path)
            
            # Check for navigation key
            if 'navigation' in obj:
                extract_recursive(obj['navigation'], current_path)
            
            # Recurse through all other keys
            for key, value in obj.items():
                if key not in ['pages', 'groups', 'tabs', 'navigation']:
                    if isinstance(value, (dict, list)):
                        extract_recursive(value, current_path)
        
        elif isinstance(obj, list):
            for item in obj:
                if isinstance(item, str):
                    pages.add(item)
                elif isinstance(item, (dict, list)):
                    extract_recursive(item, current_path)
    
    extract_recursive(data)
    return pages

def find_all_mdx_files(root_dir: Path) -> Set[str]:
    """
    Find all .mdx files in the directory tree.
    Returns a set of relative paths without the .mdx extension.
    """
    mdx_files = set()
    
    # Directories to exclude from scanning
    exclude_dirs = {'node_modules', '.git', '.github', 'api-specs', 'dictionaries', 
                   'images', 'scripts', 'site-scripts', 'logo'}
    
    for mdx_path in root_dir.rglob('*.mdx'):
        # Skip files in excluded directories
        if any(excluded in mdx_path.parts for excluded in exclude_dirs):
            continue
        
        # Get relative path from root and remove .mdx extension
        relative_path = mdx_path.relative_to(root_dir)
        path_without_extension = str(relative_path.with_suffix(''))
        mdx_files.add(path_without_extension)
    
    return mdx_files

def validate_docs(docs_json_path: Path) -> Tuple[bool, List[str], List[str]]:
    """
    Validate that docs.json and .mdx files are in sync.
    Returns: (is_valid, missing_mdx_files, orphaned_mdx_files)
    """
    root_dir = docs_json_path.parent
    
    # Load and parse docs.json
    with open(docs_json_path, 'r') as f:
        docs_data = json.load(f)
    
    # Extract all pages from docs.json
    pages_in_json = extract_pages_from_json(docs_data)
    
    # Find all .mdx files
    mdx_files = find_all_mdx_files(root_dir)
    
    # Find discrepancies
    missing_mdx = []  # Pages in docs.json but no corresponding .mdx file
    orphaned_mdx = []  # .mdx files with no entry in docs.json
    
    # Check for missing .mdx files
    for page in sorted(pages_in_json):
        mdx_path = root_dir / f"{page}.mdx"
        if not mdx_path.exists():
            missing_mdx.append(page)
    
    # Check for orphaned .mdx files
    for mdx_file in sorted(mdx_files):
        if mdx_file not in pages_in_json:
            orphaned_mdx.append(mdx_file)
    
    is_valid = len(missing_mdx) == 0 and len(orphaned_mdx) == 0
    
    return is_valid, missing_mdx, orphaned_mdx

def main():
    """Main entry point for the script."""
    # Get the path to docs.json
    script_dir = Path(__file__).parent
    repo_root = script_dir.parent.parent  # Go up from .github/scripts to repo root
    docs_json_path = repo_root / "docs.json"
    
    if not docs_json_path.exists():
        print(f"❌ Error: docs.json not found at {docs_json_path}")
        sys.exit(1)
    
    print("🔍 Validating docs.json against .mdx files...")
    print(f"   Repository root: {repo_root}")
    print()
    
    # Run validation
    is_valid, missing_mdx, orphaned_mdx = validate_docs(docs_json_path)
    
    # Report results
    if is_valid:
        print("✅ Validation successful! All pages in docs.json have corresponding .mdx files,")
        print("   and all .mdx files are referenced in docs.json.")
        sys.exit(0)
    else:
        print("❌ Validation failed! Found discrepancies:")
        print()
        
        if missing_mdx:
            print(f"📄 Pages in docs.json missing .mdx files ({len(missing_mdx)}):")
            for page in missing_mdx:
                print(f"   - {page}.mdx")
            print()
        
        if orphaned_mdx:
            print(f"🗑️  Orphaned .mdx files not in docs.json ({len(orphaned_mdx)}):")
            for mdx_file in orphaned_mdx:
                print(f"   - {mdx_file}.mdx")
            print()
        
        print("Please fix these issues to ensure documentation consistency.")
        sys.exit(1)

if __name__ == "__main__":
    main()