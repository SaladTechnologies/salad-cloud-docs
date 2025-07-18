#!/usr/bin/env python3
"""
Script to recursively verify that all referenced images exist for documentation files
within a specified directory. This script uses the verify-images.py script to check
each file individually.
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

# Thread-safe printing
print_lock = threading.Lock()


def safe_print(*args, **kwargs):
    """Thread-safe print function."""
    with print_lock:
        print(*args, **kwargs)


def find_documentation_files(directory, extensions=None):
    """
    Find all documentation files in a directory recursively.

    Args:
        directory: Path to the directory to search
        extensions: List of file extensions to include (default: common doc formats)

    Returns:
        list: List of Path objects for documentation files
    """
    if extensions is None:
        extensions = ['.md', '.mdx', '.rst', '.txt']

    directory = Path(directory)
    doc_files = []

    for ext in extensions:
        # Use glob to find files recursively
        pattern = f"**/*{ext}"
        doc_files.extend(directory.glob(pattern))

    return sorted(doc_files)


def run_image_verification(file_path, verify_script_path, workspace_root, verbose=False):
    """
    Run image verification on a single file.

    Args:
        file_path: Path to the file to verify
        verify_script_path: Path to the verify-images.py script
        workspace_root: Root directory of the workspace
        verbose: Whether to run in verbose mode

    Returns:
        dict: Result dictionary with file info and verification results
    """
    cmd = [
        sys.executable,  # Use the same Python interpreter
        str(verify_script_path),
        str(file_path)
    ]

    if workspace_root:
        cmd.extend(['--workspace-root', str(workspace_root)])

    if verbose:
        cmd.append('--verbose')

    try:
        # Run the verification script
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30  # 30 second timeout per file
        )

        return {
            'file': file_path,
            'success': result.returncode == 0,
            'returncode': result.returncode,
            'stdout': result.stdout,
            'stderr': result.stderr,
            'has_images': 'Total image references: 0' not in result.stdout
        }

    except subprocess.TimeoutExpired:
        return {
            'file': file_path,
            'success': False,
            'returncode': -1,
            'stdout': '',
            'stderr': 'Timeout: Verification took longer than 30 seconds',
            'has_images': False
        }
    except Exception as e:
        return {
            'file': file_path,
            'success': False,
            'returncode': -1,
            'stdout': '',
            'stderr': f'Error running verification: {e}',
            'has_images': False
        }


def print_file_result(result, show_success=False, show_no_images=False):
    """Print the result for a single file."""
    file_path = result['file']

    if result['success']:
        if result['has_images']:
            if show_success:
                safe_print(f"✅ {file_path}")
        else:
            if show_no_images:
                safe_print(f"📄 {file_path} (no images)")
    else:
        safe_print(f"❌ {file_path}")
        if result['stderr']:
            safe_print(f"   Error: {result['stderr']}")
        # Show relevant parts of stdout for missing images
        if 'missing image(s) found!' in result['stdout']:
            lines = result['stdout'].split('\n')
            for line in lines:
                if '❌ Missing images:' in line or line.strip().startswith('Line ') or 'Expected at:' in line:
                    safe_print(f"   {line}")


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Recursively verify image references in documentation files"
    )
    parser.add_argument(
        'directory',
        help="Directory to search for documentation files"
    )
    parser.add_argument(
        '--workspace-root',
        help="Root directory of the workspace (default: current directory)",
        default=None
    )
    parser.add_argument(
        '--extensions',
        nargs='+',
        default=['.md', '.mdx', '.rst', '.txt'],
        help="File extensions to check (default: .md .mdx .rst .txt)"
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help="Show verbose output for each file verification"
    )
    parser.add_argument(
        '--show-success',
        action='store_true',
        help="Show files that passed verification"
    )
    parser.add_argument(
        '--show-no-images',
        action='store_true',
        help="Show files that have no images"
    )
    parser.add_argument(
        '--max-workers',
        type=int,
        default=4,
        help="Maximum number of parallel workers (default: 4)"
    )
    parser.add_argument(
        '--verify-script',
        help="Path to verify-images.py script (default: auto-detect)",
        default=None
    )

    args = parser.parse_args()

    # Validate directory
    directory = Path(args.directory)
    if not directory.exists():
        print(f"Error: Directory {directory} does not exist")
        sys.exit(1)

    if not directory.is_dir():
        print(f"Error: {directory} is not a directory")
        sys.exit(1)

    # Find verify-images.py script
    if args.verify_script:
        verify_script_path = Path(args.verify_script)
    else:
        # Auto-detect: look in the same directory as this script
        script_dir = Path(__file__).parent
        verify_script_path = script_dir / 'verify-images.py'

    if not verify_script_path.exists():
        print(
            f"Error: verify-images.py script not found at {verify_script_path}")
        print("Please specify the path with --verify-script or ensure it's in the same directory")
        sys.exit(1)

    # Find documentation files
    print(f"🔍 Searching for documentation files in: {directory}")
    print(f"📁 Extensions: {', '.join(args.extensions)}")

    doc_files = find_documentation_files(directory, args.extensions)

    if not doc_files:
        print("No documentation files found!")
        sys.exit(0)

    print(f"📄 Found {len(doc_files)} documentation files")
    print(f"🔧 Using verify script: {verify_script_path}")
    print()

    # Process files in parallel
    results = []
    failed_files = []
    files_with_images = 0
    files_without_images = 0

    with ThreadPoolExecutor(max_workers=args.max_workers) as executor:
        # Submit all jobs
        future_to_file = {
            executor.submit(
                run_image_verification,
                file_path,
                verify_script_path,
                args.workspace_root,
                args.verbose
            ): file_path
            for file_path in doc_files
        }

        # Process completed jobs
        for future in as_completed(future_to_file):
            result = future.result()
            results.append(result)

            # Print result immediately
            print_file_result(result, args.show_success, args.show_no_images)

            # Track statistics
            if not result['success']:
                failed_files.append(result['file'])

            if result['has_images']:
                files_with_images += 1
            else:
                files_without_images += 1

    print()
    print("📊 Summary:")
    print(f"   Total files checked: {len(doc_files)}")
    print(f"   Files with images: {files_with_images}")
    print(f"   Files without images: {files_without_images}")
    print(f"   Files passed: {len(doc_files) - len(failed_files)}")
    print(f"   Files failed: {len(failed_files)}")

    if failed_files:
        print()
        print("❌ Files with issues:")
        for file_path in failed_files:
            print(f"   {file_path}")
        print()
        print(f"💥 {len(failed_files)} file(s) have image reference issues!")
        sys.exit(1)
    else:
        print()
        print("🎉 All image references are valid across all files!")
        sys.exit(0)


if __name__ == '__main__':
    main()
