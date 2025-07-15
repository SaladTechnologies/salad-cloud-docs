#!/usr/bin/env python3
"""
Update internal links in markdown files based on redirects defined in docs.json

This script:
1. Reads redirect mappings from docs.json
2. Finds all .md and .mdx files in the repository
3. Updates internal links to use the new paths
4. Reports changes made
"""

import json
import re
import os
import sys
import logging
from pathlib import Path
from typing import Dict, List, Tuple

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s')

def load_redirects(docs_json_path: str) -> Dict[str, str]:
    """Load redirect mappings from docs.json"""
    logging.debug(f"Loading redirects from {docs_json_path}")
    with open(docs_json_path, 'r') as f:
        docs = json.load(f)
    
    redirects = {}
    for redirect in docs.get('redirects', []):
        source = redirect.get('source', '').strip()
        destination = redirect.get('destination', '').strip()
        if source and destination:
            redirects[source] = destination
    
    logging.debug(f"Loaded {len(redirects)} redirects from docs.json")
    
    # Add additional redirects based on our recent file moves
    additional_redirects = {
        # From our recent moves - job queues now in core concepts 
        "/container-engine/explanation/job-queues": "/container-engine/explanation/core-concepts/job-queues",
        "/container-engine/explanation/external-logging": "/container-engine/explanation/core-concepts/external-logging",
        "/container-engine/explanation/disk-space": "/container-engine/explanation/container-groups/disk-space",
        "/container-engine/explanation/container-logs": "/container-engine/explanation/container-groups/container-logs", 
        "/container-engine/explanation/system-events": "/container-engine/explanation/container-groups/system-events",
        
        # Fix billing/pricing redirects that were moved
        "/container-engine/explanation/billing": "/container-engine/explanation/billing-pricing/billing",
        "/container-engine/explanation/priority-pricing": "/container-engine/explanation/billing-pricing/priority-pricing",
        "/container-engine/explanation/overview": "/container-engine/explanation/core-concepts/overview",
        "/container-engine/explanation/architectural-overview": "/container-engine/explanation/core-concepts/architectural-overview",
        "/container-engine/explanation/llm-inference-overview": "/container-engine/explanation/llm/overview",
        
        # Add common missing redirects from broken links analysis
        "/products/transcription": "/transcription/explanation/overview",
        "/products/sce": "/container-engine/explanation/core-concepts/overview",
        "/products/sgs": "/gateway-service/explanation/overview", 
        "/products/s4": "/storage/explanation/overview",
        "/products/sce/introduction": "/container-engine/explanation/core-concepts/overview",
        "/products/recipes/overview": "/container-engine/reference/recipes/overview",
        "/products/recipes": "/container-engine/reference/recipes/overview",
        "/guides": "/container-engine/explanation/core-concepts/overview",
        "/products/sce/container-groups/imds": "/container-engine/explanation/imds/introduction",
        
        # Recipe redirects
        "/products/recipes/qwen2.5-vl-7b-instruct-tgi": "/container-engine/reference/recipes/tgi",
        
        # LLM and image generation redirects
        "/guides/llm/llm-general": "/container-engine/explanation/llm/overview",
        "/guides/image-generation/": "/container-engine/explanation/image-generation/overview",
        
        # Transcription migration redirects
        "/guides/transcription/salad-transcription-api/migrate-to-salad-transcription-api/migrate-from-azure-batch": "/transcription/how-to-guides/migration/migrate-from-azure-batch",
        "/guides/transcription/salad-transcription-api/migrate-to-salad-transcription-api/migrate-from-gcp-transcription": "/transcription/how-to-guides/migration/migrate-from-gcp-transcription",
        "/guides/transcription/salad-transcription-api/migrate-to-salad-transcription-api/migrate-from-rev-transcription": "/transcription/how-to-guides/migration/migrate-from-rev-transcription",
        "/guides/transcription/salad-transcription-api/migrate-to-salad-transcription-api/migrate-from-assembly-transcription": "/transcription/how-to-guides/migration/migrate-from-assembly-transcription",
        "/guides/transcription/salad-transcription-api/migrate-to-salad-transcription-api/migrate-from-aws-transcription": "/transcription/how-to-guides/migration/migrate-from-aws-transcription",
        "/guides/transcription/salad-transcription-api/migrate-to-salad-transcription-api/migrate-from-deepgram-transcription": "/transcription/how-to-guides/migration/migrate-from-deepgram-transcription",
        
        # Image paths that need fixing
        "/products/images/salad-quickstart-1.png": "/general/images/salad-quickstart-1.png",
        "/products/images/salad-quickstart-2.png": "/general/images/salad-quickstart-2.png", 
        "/products/images/salad-quickstart-3.png": "/general/images/salad-quickstart-3.png",
        "/products/images/salad-add-payment.png": "/general/images/salad-add-payment.png",
    }
    
    # Add the additional redirects
    redirects.update(additional_redirects)
    logging.debug(f"Added {len(additional_redirects)} additional redirects")
    logging.debug(f"Total redirects available: {len(redirects)}")
    
    # Log some specific redirects we're interested in
    test_redirects = [
        '/products/sce',
        '/products/transcription', 
        '/products/s4',
        '/products/sgs',
        '/products/recipes',
        '/guides/transcription/salad-transcription-api/migrate-to-salad-transcription-api/migrate-from-azure-batch'
    ]
    
    for test_redirect in test_redirects:
        if test_redirect in redirects:
            logging.debug(f"✅ Found redirect: {test_redirect} -> {redirects[test_redirect]}")
        else:
            logging.warning(f"❌ Missing redirect: {test_redirect}")
    
    return redirects

def resolve_redirect_chain(url: str, redirects: Dict[str, str], max_depth: int = 10) -> str:
    """
    Follow redirect chains to find the final destination
    Returns the final URL after following all redirects
    """
    current_url = url
    visited = set()
    depth = 0
    
    while current_url in redirects and depth < max_depth:
        if current_url in visited:
            logging.warning(f"Circular redirect detected: {url} -> {current_url}")
            break
        
        visited.add(current_url)
        next_url = redirects[current_url]
        logging.debug(f"Redirect chain: {current_url} -> {next_url}")
        current_url = next_url
        depth += 1
    
    if depth >= max_depth:
        logging.warning(f"Max redirect depth reached for {url}")
    
    return current_url

def find_markdown_files(root_dir: str) -> List[Path]:
    """Find all markdown files in the repository"""
    markdown_files = []
    root_path = Path(root_dir)
    
    for pattern in ['**/*.md', '**/*.mdx']:
        markdown_files.extend(root_path.glob(pattern))
    
    # Filter out files in certain directories that shouldn't be processed
    excluded_dirs = {'.git', 'node_modules', '.next', 'dist', 'build'}
    
    filtered_files = []
    for file_path in markdown_files:
        if not any(excluded_dir in file_path.parts for excluded_dir in excluded_dirs):
            filtered_files.append(file_path)
    
    return filtered_files

def extract_links(content: str) -> List[Tuple[str, str, str]]:
    """
    Extract markdown links and image tags from content
    Returns list of tuples: (full_match, link_text, url)
    """
    matches = []
    
    # Pattern to match markdown links: [text](url)
    link_pattern = r'\[([^\]]*)\]\(([^)]+)\)'
    for match in re.finditer(link_pattern, content):
        full_match = match.group(0)
        link_text = match.group(1)
        url = match.group(2)
        matches.append((full_match, link_text, url))
    
    # Pattern to match HTML img tags: <img src="url" ...>
    img_pattern = r'<img\s+[^>]*src=["\']([^"\']+)["\'][^>]*>'
    for match in re.finditer(img_pattern, content):
        full_match = match.group(0)
        url = match.group(1)
        # For images, we'll use the URL as the "text" since there's no link text
        matches.append((full_match, "", url))
    
    return matches

def update_links_in_content(content: str, redirects: Dict[str, str]) -> Tuple[str, List[str]]:
    """
    Update links in content based on redirect mappings
    Returns (updated_content, list_of_changes)
    """
    changes = []
    updated_content = content
    
    links = extract_links(content)
    
    for full_match, link_text, url in links:
        # Handle URLs that might not start with / but should be internal
        processed_url = url
        
        # Add leading slash if missing for paths that look internal
        if not url.startswith(('http://', 'https://', '/', '#', 'mailto:')):
            processed_url = '/' + url
        
        # Only process internal links (starting with /)
        if processed_url.startswith('/'):
            # Handle URLs with anchors/fragments
            base_url = processed_url
            fragment = ""
            if '#' in processed_url:
                base_url, fragment = processed_url.split('#', 1)
                fragment = '#' + fragment
            
            # Remove file extensions from URLs if present
            clean_base_url = base_url
            if clean_base_url.endswith('.mdx') or clean_base_url.endswith('.md'):
                clean_base_url = clean_base_url.rsplit('.', 1)[0]
            
            # Check for redirects - try multiple variations
            redirect_found = False
            new_base_url = None
            
            # Try exact match first
            if base_url in redirects:
                new_base_url = resolve_redirect_chain(base_url, redirects)
                redirect_found = True
                logging.debug(f"Found exact redirect: {base_url} -> {new_base_url}")
            # Try without file extension
            elif clean_base_url in redirects:
                new_base_url = resolve_redirect_chain(clean_base_url, redirects)
                redirect_found = True
                logging.debug(f"Found clean redirect: {clean_base_url} -> {new_base_url}")
            # Try with trailing slash removed
            elif base_url.rstrip('/') in redirects:
                new_base_url = resolve_redirect_chain(base_url.rstrip('/'), redirects)
                redirect_found = True
                logging.debug(f"Found trimmed redirect: {base_url.rstrip('/')} -> {new_base_url}")
            # Try clean URL without trailing slash
            elif clean_base_url.rstrip('/') in redirects:
                new_base_url = resolve_redirect_chain(clean_base_url.rstrip('/'), redirects)
                redirect_found = True
                logging.debug(f"Found clean trimmed redirect: {clean_base_url.rstrip('/')} -> {new_base_url}")
            else:
                logging.debug(f"No redirect found for: {base_url}")
            
            if redirect_found and new_base_url:
                new_url = new_base_url + fragment
                
                # Handle different types of replacements
                if '<img' in full_match:
                    # For image tags, replace the src attribute
                    new_link = full_match.replace(f'src="{url}"', f'src="{new_url}"').replace(f"src='{url}'", f"src='{new_url}'")
                else:
                    # For markdown links
                    new_link = f'[{link_text}]({new_url})'
                
                updated_content = updated_content.replace(full_match, new_link)
                changes.append(f"  {processed_url} → {new_url}")
    
    return updated_content, changes

def process_file(file_path: Path, redirects: Dict[str, str]) -> Tuple[bool, List[str]]:
    """
    Process a single markdown file
    Returns (was_modified, list_of_changes)
    """
    try:
        logging.debug(f"Processing file: {file_path}")
        with open(file_path, 'r', encoding='utf-8') as f:
            original_content = f.read()
        
        # Extract links to see what we're working with
        links = extract_links(original_content)
        if links:
            logging.debug(f"Found {len(links)} links in {file_path}")
            for full_match, link_text, url in links[:5]:  # Log first 5 links
                logging.debug(f"  Link: {url}")
        
        updated_content, changes = update_links_in_content(original_content, redirects)
        
        if changes:
            logging.debug(f"Making {len(changes)} changes to {file_path}")
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(updated_content)
            return True, changes
        
        return False, []
        
    except Exception as e:
        logging.error(f"Error processing {file_path}: {e}")
        return False, []

def main():
    """Main function"""
    if len(sys.argv) > 1:
        root_dir = sys.argv[1]
    else:
        root_dir = '.'
    
    docs_json_path = os.path.join(root_dir, 'docs.json')
    
    if not os.path.exists(docs_json_path):
        print(f"Error: docs.json not found at {docs_json_path}")
        sys.exit(1)
    
    print("🔄 Loading redirects from docs.json...")
    redirects = load_redirects(docs_json_path)
    print(f"📋 Found {len(redirects)} redirect mappings")
    
    print("🔍 Finding markdown files...")
    markdown_files = find_markdown_files(root_dir)
    print(f"📄 Found {len(markdown_files)} markdown files to process")
    
    total_modified = 0
    total_changes = 0
    
    print("\n🚀 Processing files...")
    
    # Target files with known broken links
    broken_link_files = [
        'general/explanation/overview.mdx',
        'general/tutorials/account-setup.mdx'
    ]
    
    for file_path in markdown_files:
        rel_path = file_path.relative_to(Path(root_dir))
        
        # Add extra logging for files with known broken links
        if str(rel_path) in broken_link_files:
            logging.info(f"🎯 Processing file with known broken links: {rel_path}")
        
        was_modified, changes = process_file(file_path, redirects)
        
        if was_modified:
            total_modified += 1
            total_changes += len(changes)
            rel_path = file_path.relative_to(Path(root_dir))
            print(f"✅ Updated {rel_path}:")
            for change in changes:
                print(change)
            print()
    
    print("📊 Summary:")
    print(f"  Files processed: {len(markdown_files)}")
    print(f"  Files modified: {total_modified}")
    print(f"  Total link updates: {total_changes}")
    
    if total_modified == 0:
        print("✨ No files needed updating - all links are current!")
    else:
        print(f"✨ Successfully updated {total_changes} links in {total_modified} files!")

if __name__ == "__main__":
    main()
