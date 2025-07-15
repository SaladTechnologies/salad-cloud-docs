#!/usr/bin/env python3

"""
Script to move a documentation file from old structure to new DiATaxis structure.

This script:
1. Moves a file using git mv (preserves history)
2. Updates docs.json to remove old navigation reference
3. Adds new navigation reference in appropriate DiATaxis category
4. Adds redirect from old URL to new URL

Usage:
    python move-file.py <source_path> <dest_path>

Example:
    python move-file.py products/sce/getting-started/quickstart.mdx container-engine/tutorials/quickstart.mdx

Arguments:
    source_path: Relative path to the source file (from repo root)
    dest_path: Relative path to the destination file (from repo root)
"""

import sys
import os
import json
import subprocess
import re
import shutil
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Set


def run_command(cmd: List[str], cwd: Optional[str] = None) -> Tuple[int, str, str]:
    """Run a shell command and return exit code, stdout, stderr."""
    try:
        result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        return 1, "", str(e)


def ensure_directory_exists(file_path: str) -> None:
    """Create directory structure if it doesn't exist."""
    directory = os.path.dirname(file_path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)
        print(f"Created directory: {directory}")


def git_move_file(source: str, dest: str) -> bool:
    """Move file using git mv to preserve history."""
    # Ensure destination directory exists
    ensure_directory_exists(dest)

    # Use git mv to preserve file history
    exit_code, stdout, stderr = run_command(["git", "mv", source, dest])

    if exit_code == 0:
        print(f"✅ Moved file: {source} → {dest}")
        return True
    else:
        print(f"❌ Failed to move file: {stderr}")
        return False


def find_image_references(file_path: str) -> Set[str]:
    """Find all image references in a markdown file."""
    if not os.path.exists(file_path):
        return set()

    image_refs = set()

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Find markdown image syntax: ![alt](path)
        md_images = re.findall(r'!\[.*?\]\(([^)]+)\)', content)
        image_refs.update(md_images)

        # Find HTML img tags: <img src="path" />
        html_images = re.findall(r'<img[^>]+src=["\']([^"\']+)["\']', content)
        image_refs.update(html_images)

        # Filter to include relative paths and absolute paths that are local files
        local_images = set()
        for img_path in image_refs:
            # Skip URLs and data URIs
            if img_path.startswith(('http://', 'https://', 'data:')):
                continue
            # Include relative paths and absolute paths that point to local files
            local_images.add(img_path)

        return local_images

    except Exception as e:
        print(f"⚠️  Error reading file for image references: {e}")
        return set()


def resolve_image_path(doc_path: str, image_ref: str) -> Optional[str]:
    """Resolve relative or absolute image path to absolute path from repo root."""
    # If it's an absolute path starting with /, treat it as relative to repo root
    if image_ref.startswith('/'):
        abs_image_path = image_ref[1:]  # Remove leading slash
    else:
        # It's a relative path, resolve relative to document directory
        doc_dir = os.path.dirname(doc_path)
        if doc_dir:
            abs_image_path = os.path.normpath(os.path.join(doc_dir, image_ref))
        else:
            abs_image_path = image_ref

    # Check if file exists
    if os.path.exists(abs_image_path):
        return abs_image_path

    return None


def determine_new_image_path(old_doc_path: str, new_doc_path: str, image_path: str) -> str:
    """Determine where an image should be moved in the new structure."""
    # Get the product from the new document path
    new_path_parts = new_doc_path.split('/')
    if len(new_path_parts) < 1:
        raise ValueError(f"Invalid new document path: {new_doc_path}")

    product = new_path_parts[0]  # e.g., 'container-engine'

    # Get the image filename
    image_filename = os.path.basename(image_path)

    # New image path: {product}/images/{filename}
    new_image_path = f"{product}/images/{image_filename}"

    return new_image_path


def move_image_file(old_path: str, new_path: str) -> bool:
    """Move an image file using git mv."""
    # Ensure destination directory exists
    ensure_directory_exists(new_path)

    # Use git mv to preserve file history
    exit_code, stdout, stderr = run_command(["git", "mv", old_path, new_path])

    if exit_code == 0:
        print(f"  📷 Moved image: {old_path} → {new_path}")
        return True
    else:
        # If git mv fails, try regular copy (might be a new file)
        try:
            shutil.copy2(old_path, new_path)
            # Add to git
            run_command(["git", "add", new_path])
            print(f"  📷 Copied image: {old_path} → {new_path}")
            return True
        except Exception as e:
            print(f"  ❌ Failed to move image {old_path}: {e}")
            return False


def update_image_references_in_file(file_path: str, image_mapping: Dict[str, str]) -> bool:
    """Update image and media references in a file based on the mapping."""
    if not os.path.exists(file_path):
        return False

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        original_content = content

        # Update each image/media reference
        for old_ref, new_ref in image_mapping.items():
            # Update markdown image syntax
            content = re.sub(
                r'(!\[.*?\]\()' + re.escape(old_ref) + r'(\))',
                r'\1' + new_ref + r'\2',
                content
            )

            # Update HTML img tags
            content = re.sub(
                r'(<img[^>]+src=["\'])' + re.escape(old_ref) + r'(["\'])',
                r'\1' + new_ref + r'\2',
                content
            )

            # Update video tags (HTML5 video)
            content = re.sub(
                r'(<video[^>]+src=["\'])' + re.escape(old_ref) + r'(["\'])',
                r'\1' + new_ref + r'\2',
                content
            )

            # Update meta tags (og:image, twitter:image, etc.)
            content = re.sub(
                r"('[^']*image':\s*['\"])(" + re.escape(old_ref) + r")(['\"])",
                r'\1' + new_ref + r'\3',
                content
            )

            # Update Frame components with img tags inside
            content = re.sub(
                r'(<Frame[^>]*>\s*<img[^>]+src=["\'])' +
                re.escape(old_ref) + r'(["\'])',
                r'\1' + new_ref + r'\2',
                content
            )

        # Also handle general /guides/ path updates to /container-engine/images/
        # This catches any remaining /guides/ image references that weren't in our mapping
        content = re.sub(
            r'(/guides/[^/]+/images/[^"\'\s)]+)',
            lambda m: '/container-engine/images/' +
            os.path.basename(m.group(1)),
            content
        )

        # Only write if content changed
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"  📝 Updated image/media references in: {file_path}")
            return True

        return True

    except Exception as e:
        print(f"  ❌ Error updating image references: {e}")
        return False


def process_images(source_path: str, dest_path: str) -> bool:
    """Process all images referenced by the document."""
    print("🖼️  Processing images...")

    # Find all image references in the destination file (after it's been moved)
    image_refs = find_image_references(dest_path)

    if not image_refs:
        print("  ℹ️  No images found in document")
        return True

    print(f"  Found {len(image_refs)} image references")

    image_mapping = {}  # old_ref -> new_ref
    images_to_move = []  # (old_path, new_path)

    # Process each image reference
    for image_ref in image_refs:
        # Resolve to actual file path using the original source path structure
        actual_image_path = resolve_image_path(source_path, image_ref)

        if not actual_image_path:
            print(f"  ⚠️  Image not found: {image_ref}")
            continue

        # Determine new image location
        try:
            new_image_path = determine_new_image_path(
                source_path, dest_path, actual_image_path)
        except ValueError as e:
            print(f"  ❌ {e}")
            continue

        # Calculate new image reference based on original reference type
        if image_ref.startswith('/'):
            # Original was absolute doc path, keep it absolute but update location
            new_image_ref = f"/{new_image_path}"
        else:
            # Original was relative, make it relative from new document location
            new_doc_dir = os.path.dirname(dest_path)
            if new_doc_dir:
                new_image_ref = os.path.relpath(new_image_path, new_doc_dir)
            else:
                new_image_ref = new_image_path
            # Normalize path separators for consistency
            new_image_ref = new_image_ref.replace('\\', '/')

        image_mapping[image_ref] = new_image_ref
        images_to_move.append((actual_image_path, new_image_path))

    # Move all images
    for old_path, new_path in images_to_move:
        if not os.path.exists(new_path):  # Avoid duplicate moves
            if not move_image_file(old_path, new_path):
                return False
        else:
            print(f"  ⚠️  Image already exists at destination: {new_path}")

    # Update image references in the destination file (after it's been moved)
    if image_mapping:
        if not update_image_references_in_file(dest_path, image_mapping):
            return False

    print(f"✅ Processed {len(images_to_move)} images")
    return True


def path_to_url(file_path: str) -> str:
    """Convert file path to URL path (remove .mdx extension)."""
    if file_path.endswith('.mdx'):
        return file_path[:-4]  # Remove .mdx extension
    return file_path


def remove_page_from_navigation(nav_data: Dict, page_path: str) -> bool:
    """Recursively remove a page from navigation structure."""
    def remove_from_group(group: Dict) -> bool:
        if 'pages' in group:
            # Check if page is directly in this group's pages
            if page_path in group['pages']:
                group['pages'].remove(page_path)
                print(f"✅ Removed page from navigation: {page_path}")
                return True

            # Check nested groups
            for i, item in enumerate(group['pages']):
                if isinstance(item, dict) and 'group' in item:
                    if remove_from_group(item):
                        # If the nested group is now empty, remove it
                        if not item.get('pages'):
                            group['pages'].pop(i)
                        return True
        return False

    # Search through all tabs and groups
    for tab in nav_data.get('tabs', []):
        for group in tab.get('groups', []):
            if remove_from_group(group):
                return True

    return False


def determine_nav_location(dest_path: str) -> Tuple[str, str, Optional[str]]:
    """
    Determine which tab, group, and subgroup a file should go in based on its destination path.

    Returns: (tab_name, group_name, subgroup_name)
    """
    path_parts = dest_path.split('/')

    if len(path_parts) < 2:
        raise ValueError(f"Invalid destination path: {dest_path}")

    product = path_parts[0]
    category = path_parts[1]
    # Only create subgroup if there are 4+ parts (product/category/subgroup/file)
    subgroup = path_parts[2] if len(path_parts) > 3 else None

    # Map product directories to tab names
    product_to_tab = {
        'general': 'General',
        'container-engine': 'Container Engine',
        'transcription': 'Transcription',
        'gateway-service': 'Gateway Service',
        'storage': 'Storage'
    }

    # Map DiATaxis categories to group names
    category_to_group = {
        'tutorials': 'Tutorials',
        'how-to-guides': 'How-to Guides',
        'explanation': 'Explanation',
        'reference': 'Reference'
    }

    tab_name = product_to_tab.get(product)
    group_name = category_to_group.get(category)

    if not tab_name:
        raise ValueError(f"Unknown product: {product}")
    if not group_name:
        raise ValueError(f"Unknown category: {category}")

    # Capitalize subgroup name if it exists
    subgroup_name = subgroup.replace('-', ' ').title() if subgroup else None

    return tab_name, group_name, subgroup_name


def add_page_to_navigation(nav_data: Dict, dest_path: str) -> bool:
    """Add page to the appropriate location in navigation."""
    try:
        tab_name, group_name, subgroup_name = determine_nav_location(dest_path)
    except ValueError as e:
        print(f"❌ {e}")
        return False

    # Ensure navigation structure exists
    if 'tabs' not in nav_data:
        nav_data['tabs'] = []

    # Find or create the target tab
    target_tab = None
    for tab in nav_data['tabs']:
        if tab.get('tab') == tab_name:
            target_tab = tab
            break

    if not target_tab:
        # Create new tab
        target_tab = {
            "tab": tab_name,
            "groups": []
        }
        nav_data['tabs'].append(target_tab)
        print(f"✅ Created new tab: {tab_name}")

    # Ensure groups array exists
    if 'groups' not in target_tab:
        target_tab['groups'] = []

    # Find or create the target group
    target_group = None
    for group in target_tab['groups']:
        if group.get('group') == group_name:
            target_group = group
            break

    if not target_group:
        # Create new group
        target_group = {
            "group": group_name,
            "pages": []
        }
        target_tab['groups'].append(target_group)
        print(f"✅ Created new group: {group_name} in {tab_name}")

    # Ensure pages array exists
    if 'pages' not in target_group:
        target_group['pages'] = []

    # Handle subgroups if needed
    if subgroup_name:
        # Find or create the target subgroup
        target_subgroup = None
        for item in target_group['pages']:
            if isinstance(item, dict) and item.get('group') == subgroup_name:
                target_subgroup = item
                break

        if not target_subgroup:
            # Create new subgroup
            target_subgroup = {
                "group": subgroup_name,
                "pages": []
            }
            target_group['pages'].append(target_subgroup)
            print(
                f"✅ Created new subgroup: {subgroup_name} in {tab_name} > {group_name}")

        # Ensure subgroup pages array exists
        if 'pages' not in target_subgroup:
            target_subgroup['pages'] = []

        # Add the page to the subgroup
        page_url = path_to_url(dest_path)
        target_subgroup['pages'].append(page_url)
        print(
            f"✅ Added page to navigation: {page_url} in {tab_name} > {group_name} > {subgroup_name}")
    else:
        # Add the page directly to the group
        page_url = path_to_url(dest_path)
        target_group['pages'].append(page_url)
        print(
            f"✅ Added page to navigation: {page_url} in {tab_name} > {group_name}")

    return True


def add_redirect(redirects: List[Dict], source_path: str, dest_path: str) -> None:
    """Add redirect from old URL to new URL."""
    source_url = "/" + path_to_url(source_path)
    dest_url = "/" + path_to_url(dest_path)

    # Check if redirect already exists
    for redirect in redirects:
        if redirect.get('source') == source_url:
            print(f"⚠️  Redirect already exists: {source_url}")
            return

    redirect = {
        "source": source_url,
        "destination": dest_url
    }

    redirects.append(redirect)
    print(f"✅ Added redirect: {source_url} → {dest_url}")


def update_docs_json(source_path: str, dest_path: str) -> bool:
    """Update docs.json with navigation changes and redirects."""
    docs_json_path = "docs.json"

    if not os.path.exists(docs_json_path):
        print(f"❌ docs.json not found at {docs_json_path}")
        return False

    # Load docs.json
    try:
        with open(docs_json_path, 'r', encoding='utf-8') as f:
            docs_data = json.load(f)
    except Exception as e:
        print(f"❌ Failed to load docs.json: {e}")
        return False

    # Remove old navigation reference
    source_url = path_to_url(source_path)
    removed = remove_page_from_navigation(
        docs_data.get('navigation', {}), source_url)
    if not removed:
        print(f"⚠️  Page not found in navigation: {source_url}")

    # Add new navigation reference
    nav_added = add_page_to_navigation(
        docs_data.get('navigation', {}), dest_path)
    if not nav_added:
        print(f"❌ Failed to add page to navigation")
        return False

    # Add redirect
    if 'redirects' not in docs_data:
        docs_data['redirects'] = []

    add_redirect(docs_data['redirects'], source_path, dest_path)

    # Save updated docs.json
    try:
        with open(docs_json_path, 'w', encoding='utf-8') as f:
            json.dump(docs_data, f, indent=2, ensure_ascii=False)
        print(f"✅ Updated docs.json")
        return True
    except Exception as e:
        print(f"❌ Failed to save docs.json: {e}")
        return False


def validate_paths(source_path: str, dest_path: str) -> bool:
    """Validate source and destination paths."""
    if not os.path.exists(source_path):
        print(f"❌ Source file does not exist: {source_path}")
        return False

    if os.path.exists(dest_path):
        print(f"❌ Destination file already exists: {dest_path}")
        return False

    if not source_path.endswith('.mdx'):
        print(f"❌ Source file must be a .mdx file: {source_path}")
        return False

    if not dest_path.endswith('.mdx'):
        print(f"❌ Destination file must be a .mdx file: {dest_path}")
        return False

    return True


def main():
    if len(sys.argv) != 3:
        print("Usage: python move-file.py <source_path> <dest_path>")
        print("\nExample:")
        print("  python move-file.py products/sce/getting-started/quickstart.mdx container-engine/tutorials/quickstart.mdx")
        print("\nThis script will:")
        print("  1. Move the document file using git mv")
        print("  2. Find and move all referenced images")
        print("  3. Update image references in the document")
        print("  4. Update docs.json navigation and add redirects")
        sys.exit(1)

    source_path = sys.argv[1]
    dest_path = sys.argv[2]

    print(f"📁 Moving file: {source_path} → {dest_path}")
    print("-" * 60)

    # Validate paths
    if not validate_paths(source_path, dest_path):
        sys.exit(1)

    # Move the file with git
    if not git_move_file(source_path, dest_path):
        sys.exit(1)

    # Process images (after the main file is moved)
    if not process_images(source_path, dest_path):
        print("❌ Failed to process images - you may need to review image moves manually")
        # Don't exit here, continue with docs.json update

    # Update docs.json
    if not update_docs_json(source_path, dest_path):
        print("❌ Failed to update docs.json - you may need to revert the file move")
        sys.exit(1)

    print("-" * 60)
    print("✅ File move completed successfully!")
    print(f"📄 File moved: {source_path} → {dest_path}")
    print(f"🖼️  Images processed and moved to new structure")
    print(f"📝 docs.json updated with navigation changes and redirect")


if __name__ == "__main__":
    main()
