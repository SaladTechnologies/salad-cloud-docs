#!/usr/bin/env python3
"""
Script to analyze navigation structure vs actual file structure.
Identifies missing files and navigation entries that don't correspond to actual files.
"""

import json
import os
from pathlib import Path
from typing import Set, List, Dict, Any


def extract_page_paths(docs_data: Any) -> Set[str]:
    """Recursively extract all page paths from navigation structure."""
    paths = set()
    
    def traverse(data):
        if isinstance(data, str):
            paths.add(data)
        elif isinstance(data, dict):
            if 'pages' in data:
                traverse(data['pages'])
            elif 'groups' in data:
                traverse(data['groups'])
        elif isinstance(data, list):
            for item in data:
                traverse(item)
    
    # Navigate to the navigation.tabs structure
    if 'navigation' in docs_data and 'tabs' in docs_data['navigation']:
        traverse(docs_data['navigation']['tabs'])
    
    return paths


def find_actual_files() -> Set[str]:
    """Find all actual .mdx files in the workspace."""
    mdx_files = set()
    
    # Walk through all directories
    for root, dirs, files in os.walk('.'):
        # Skip certain directories
        skip_dirs = {'.git', 'node_modules', '__pycache__', 'scripts', 'site-scripts', 'api-specs', 'dictionaries', 'logo', 'shared'}
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        
        for file in files:
            if file.endswith('.mdx'):
                # Convert to relative path without .mdx extension
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, '.').replace('\\', '/')
                # Remove .mdx extension
                path_without_ext = relative_path[:-4]
                mdx_files.add(path_without_ext)
    
    return mdx_files


def main():
    """Main function to analyze navigation vs file structure."""
    # Load docs.json
    with open('docs.json', 'r') as f:
        docs_data = json.load(f)
    
    # Extract navigation paths
    nav_paths = extract_page_paths(docs_data)
    
    # Find actual files
    actual_files = find_actual_files()
    
    print("=== NAVIGATION STRUCTURE ANALYSIS ===\n")
    
    print(f"📊 SUMMARY:")
    print(f"  Navigation entries: {len(nav_paths)}")
    print(f"  Actual MDX files: {len(actual_files)}")
    print()
    
    # Find navigation entries without corresponding files
    missing_files = nav_paths - actual_files
    if missing_files:
        print(f"❌ NAVIGATION ENTRIES WITHOUT FILES ({len(missing_files)}):")
        for path in sorted(missing_files):
            print(f"  - {path}")
        print()
    else:
        print("✅ All navigation entries have corresponding files!")
        print()
    
    # Find files not referenced in navigation
    orphaned_files = actual_files - nav_paths
    if orphaned_files:
        print(f"📁 FILES NOT IN NAVIGATION ({len(orphaned_files)}):")
        for path in sorted(orphaned_files):
            print(f"  - {path}")
        print()
    else:
        print("✅ All files are referenced in navigation!")
        print()
    
    # Analyze by section
    print("📂 ANALYSIS BY SECTION:")
    
    sections = {
        'General': [],
        'Container Engine': [],
        'Transcription': [],
        'Gateway Service': [],
        'Storage': [],
        'API Reference': []
    }
    
    for path in nav_paths:
        if path.startswith('general/'):
            sections['General'].append(path)
        elif path.startswith('container-engine/'):
            sections['Container Engine'].append(path)
        elif path.startswith('transcription/'):
            sections['Transcription'].append(path)
        elif path.startswith('gateway-service/'):
            sections['Gateway Service'].append(path)
        elif path.startswith('storage/'):
            sections['Storage'].append(path)
        elif path.startswith('reference/'):
            sections['API Reference'].append(path)
    
    for section, paths in sections.items():
        if paths:
            missing_in_section = [p for p in paths if p in missing_files]
            print(f"\n  {section}: {len(paths)} entries")
            if missing_in_section:
                print(f"    ❌ Missing files: {len(missing_in_section)}")
                for path in sorted(missing_in_section):
                    print(f"      - {path}")
            else:
                print(f"    ✅ All files exist")
    
    print("\n=== RECOMMENDATIONS ===")
    
    if missing_files:
        print("\n🔧 TO FIX MISSING FILES:")
        print("  1. Create the missing files, or")
        print("  2. Remove entries from docs.json navigation")
        
        # Group by common patterns
        container_engine_missing = [p for p in missing_files if p.startswith('container-engine/')]
        if container_engine_missing:
            print(f"\n  Container Engine missing files ({len(container_engine_missing)}):")
            for path in sorted(container_engine_missing):
                print(f"    - {path}")
    
    if orphaned_files:
        print(f"\n📋 TO ADD ORPHANED FILES:")
        print("  Consider adding these files to navigation if they should be accessible:")
        
        # Group orphaned files by section
        orphaned_by_section = {}
        for path in orphaned_files:
            section = path.split('/')[0] if '/' in path else 'root'
            if section not in orphaned_by_section:
                orphaned_by_section[section] = []
            orphaned_by_section[section].append(path)
        
        for section, paths in sorted(orphaned_by_section.items()):
            print(f"\n  {section.title()}: {len(paths)} files")
            for path in sorted(paths):
                print(f"    - {path}")


if __name__ == '__main__':
    main()
