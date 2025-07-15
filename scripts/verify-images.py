#!/usr/bin/env python3
"""
Script to verify that all referenced images exist for a given documentation file.
This script checks both absolute and relative image paths in markdown files.
"""

import argparse
import os
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

def extract_image_references(file_path):
    """
    Extract all image references from a markdown file.
    
    Args:
        file_path: Path to the markdown file
        
    Returns:
        list: List of tuples (line_number, image_path, full_line)
    """
    image_references = []
    
    # Regular expressions for different image syntax patterns
    patterns = [
        # Standard markdown: ![alt](path)
        r'!\[([^\]]*)\]\(([^)]+)\)',
        # HTML img tags: <img src="path" />
        r'<img[^>]+src=[\'"]([^\'"]+)[\'"][^>]*>',
        # MDX/JSX img: <img src="path" />
        r'<img[^>]+src=\{[\'"]([^\'"]+)[\'"]\}[^>]*>',
        # Direct image references in some contexts
        r'image:\s*[\'"]([^\'"]+)[\'"]',
    ]
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                for pattern in patterns:
                    matches = re.finditer(pattern, line, re.IGNORECASE)
                    for match in matches:
                        # Extract the image path from the match groups
                        groups = match.groups()
                        if len(groups) >= 2:
                            # For markdown syntax ![alt](path), path is the second group
                            image_path = groups[1] if pattern.startswith(r'!\[') else groups[0]
                        else:
                            image_path = groups[0] if groups else match.group(1)
                        
                        image_references.append((line_num, image_path.strip(), line.strip()))
    
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return []
    
    return image_references

def is_external_url(path):
    """Check if a path is an external URL."""
    parsed = urlparse(path)
    return bool(parsed.scheme in ['http', 'https'])

def resolve_image_path(image_path, file_path, workspace_root):
    """
    Resolve the actual file system path for an image reference.
    
    Args:
        image_path: The image path as found in the file
        file_path: Path to the file containing the reference
        workspace_root: Root directory of the workspace
        
    Returns:
        Path object or None if external URL
    """
    # Skip external URLs
    if is_external_url(image_path):
        return None
    
    # Remove any URL fragments or query parameters
    clean_path = image_path.split('#')[0].split('?')[0]
    
    # Handle absolute paths (starting with /)
    if clean_path.startswith('/'):
        # Absolute path from workspace root
        return workspace_root / clean_path.lstrip('/')
    
    # Handle relative paths
    file_dir = Path(file_path).parent
    return file_dir / clean_path

def verify_images(file_path, workspace_root=None):
    """
    Verify all image references in a file.
    
    Args:
        file_path: Path to the file to check
        workspace_root: Root directory of the workspace (defaults to current directory)
        
    Returns:
        tuple: (total_images, missing_images, external_images, results)
    """
    if workspace_root is None:
        workspace_root = Path.cwd()
    else:
        workspace_root = Path(workspace_root)
    
    file_path = Path(file_path)
    
    if not file_path.exists():
        print(f"Error: File {file_path} does not exist")
        return 0, 0, 0, []
    
    print(f"🔍 Checking image references in: {file_path}")
    print(f"📁 Workspace root: {workspace_root}")
    print()
    
    image_references = extract_image_references(file_path)
    
    if not image_references:
        print("✅ No image references found in file")
        return 0, 0, 0, []
    
    results = []
    missing_images = []
    external_images = []
    
    for line_num, image_path, line in image_references:
        # Check if it's an external URL
        if is_external_url(image_path):
            external_images.append((line_num, image_path, line))
            results.append({
                'line': line_num,
                'path': image_path,
                'status': 'external',
                'resolved_path': None,
                'line_content': line
            })
            continue
        
        # Resolve the actual file path
        resolved_path = resolve_image_path(image_path, file_path, workspace_root)
        
        if resolved_path and resolved_path.exists():
            status = 'found'
        else:
            status = 'missing'
            missing_images.append((line_num, image_path, resolved_path, line))
        
        results.append({
            'line': line_num,
            'path': image_path,
            'status': status,
            'resolved_path': resolved_path,
            'line_content': line
        })
    
    return len(image_references), len(missing_images), len(external_images), results

def print_results(total_images, missing_images, external_images, results, verbose=False):
    """Print the verification results."""
    
    print(f"📊 Summary:")
    print(f"   Total image references: {total_images}")
    print(f"   External URLs: {external_images}")
    print(f"   Local images found: {total_images - missing_images - external_images}")
    print(f"   Missing images: {missing_images}")
    print()
    
    if verbose or missing_images > 0:
        # Group results by status
        found_images = [r for r in results if r['status'] == 'found']
        missing_image_results = [r for r in results if r['status'] == 'missing']
        external_image_results = [r for r in results if r['status'] == 'external']
        
        if found_images and verbose:
            print("✅ Found images:")
            for result in found_images:
                print(f"   Line {result['line']}: {result['path']}")
                if result['resolved_path']:
                    print(f"      → {result['resolved_path']}")
            print()
        
        if external_image_results and verbose:
            print("🌐 External image URLs:")
            for result in external_image_results:
                print(f"   Line {result['line']}: {result['path']}")
            print()
        
        if missing_image_results:
            print("❌ Missing images:")
            for result in missing_image_results:
                print(f"   Line {result['line']}: {result['path']}")
                if result['resolved_path']:
                    print(f"      → Expected at: {result['resolved_path']}")
                print(f"      → Line content: {result['line_content'][:100]}...")
            print()

def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Verify that all referenced images exist in a documentation file"
    )
    parser.add_argument(
        'file',
        help="Path to the file to check for image references"
    )
    parser.add_argument(
        '--workspace-root',
        help="Root directory of the workspace (default: current directory)",
        default=None
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help="Show all image references, not just missing ones"
    )
    
    args = parser.parse_args()
    
    try:
        total_images, missing_images, external_images, results = verify_images(
            args.file, 
            args.workspace_root
        )
        
        print_results(total_images, missing_images, external_images, results, args.verbose)
        
        if missing_images > 0:
            print(f"💥 {missing_images} missing image(s) found!")
            sys.exit(1)
        else:
            print("🎉 All local image references are valid!")
            sys.exit(0)
            
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
