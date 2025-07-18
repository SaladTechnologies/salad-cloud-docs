#!/usr/bin/env python3
"""
Script to fix cross-references between files that still point to old /guides/ paths
"""

import os
import re
import argparse
from pathlib import Path


def create_reference_mapping():
    """Create a mapping of old /guides/ paths to new container-engine paths"""
    return {
        # Image Generation guides
        "/guides/image-generation/": "/container-engine/how-to-guides/image-generation/",

        # Computer Vision guides
        "/guides/computer-vision/": "/container-engine/how-to-guides/computer-vision/",
        "/guides/computer-vision/yolov8/": "/container-engine/tutorials/computer-vision/",

        # LLM guides
        "/guides/llm/": "/container-engine/how-to-guides/llm/",

        # Transcription guides (some moved to transcription tab, some to container-engine)
        "/guides/transcription/youtube": "/container-engine/how-to-guides/transcription/youtube-transcription-pipeline",
        "/guides/transcription/": "/transcription/how-to-guides/",

        # Long-running tasks
        "/guides/long-running-tasks/": "/container-engine/explanation/long-running-tasks/",
        "/guides/long-running-tasks/solution-overview": "/container-engine/explanation/long-running-tasks/solution-overview",
        "/guides/long-running-tasks/kelpie": "/container-engine/how-to-guides/long-running-tasks/kelpie",
        "/guides/long-running-tasks/gcp-pub-sub": "/container-engine/how-to-guides/long-running-tasks/gcp-pub-sub",
        "/guides/long-running-tasks/rabbitmq": "/container-engine/how-to-guides/long-running-tasks/rabbitmq",
        "/guides/long-running-tasks/sqs": "/container-engine/how-to-guides/long-running-tasks/sqs",

        # Real-time inference
        "/guides/real-time-inference/": "/container-engine/how-to-guides/real-time-inference/",
        "/guides/real-time-inference/use-container-gateway": "/container-engine/how-to-guides/real-time-inference/use-container-gateway",
        "/guides/real-time-inference/build-redis-queue": "/container-engine/how-to-guides/real-time-inference/build-redis-queue",

        # Kubernetes integration
        "/guides/kubernetes-integration/": "/container-engine/explanation/kubernetes-integration/",
        "/guides/kubernetes-integration/solution-overview": "/container-engine/explanation/kubernetes-integration/solution-overview",
        "/guides/kubernetes-integration/installation-helm-chart": "/container-engine/how-to-guides/kubernetes-integration/installation-helm-chart",
        "/guides/kubernetes-integration/application-deployment": "/container-engine/how-to-guides/kubernetes-integration/application-deployment",
        "/guides/kubernetes-integration/service-access": "/container-engine/how-to-guides/kubernetes-integration/service-access",

        # Tailscale integration
        "/guides/tailscale-integration/": "/container-engine/explanation/tailscale-integration/",
        "/guides/tailscale-integration/solution-overview": "/container-engine/explanation/tailscale-integration/solution-overview",
        "/guides/tailscale-integration/basic": "/container-engine/how-to-guides/tailscale-integration/basic",

        # Molecular dynamics
        "/guides/molecular-dynamics-simulation/": "/container-engine/how-to-guides/molecular-dynamics-simulation/",
        "/guides/molecular-dynamics-simulation/gromacs-srcg": "/container-engine/how-to-guides/molecular-dynamics-simulation/gromacs-srcg",

        # Audio processing
        "/guides/text-to-speech/": "/container-engine/how-to-guides/audio-processing/",
        "/guides/text-to-speech/metavoice-tts-voice-cloning": "/container-engine/how-to-guides/audio-processing/metavoice-tts-voice-cloning",
        "/guides/text-to-speech/openvoice-tts-voice-cloning": "/container-engine/how-to-guides/audio-processing/openvoice-tts-voice-cloning",

        # Troubleshooting
        "/guides/troubleshooting": "/container-engine/how-to-guides/troubleshooting",
    }


def fix_cross_references_in_file(file_path, mapping):
    """Fix cross-references in a single file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        original_content = content
        changes_made = []

        # Sort mappings by length (longest first) to avoid partial replacements
        sorted_mappings = sorted(
            mapping.items(), key=lambda x: len(x[0]), reverse=True)

        for old_path, new_path in sorted_mappings:
            # Look for various forms of references
            patterns = [
                # Markdown links [text](path)
                rf'\[([^\]]*)\]\({re.escape(old_path)}([^)]*)\)',
                # Direct references in quotes
                rf'"{re.escape(old_path)}([^"]*)"',
                rf"'{re.escape(old_path)}([^']*)'",
                # HTML href attributes
                rf'href="{re.escape(old_path)}([^"]*)"',
                rf"href='{re.escape(old_path)}([^']*)'",
            ]

            for pattern in patterns:
                matches = list(re.finditer(pattern, content))
                # Process in reverse to maintain positions
                for match in reversed(matches):
                    if pattern.startswith(r'\['):
                        # Markdown link
                        link_text = match.group(1)
                        remaining_path = match.group(2)
                        replacement = f'[{link_text}]({new_path}{remaining_path})'
                    elif 'href=' in pattern:
                        # HTML href
                        remaining_path = match.group(1)
                        quote_char = '"' if '"{' in pattern else "'"
                        replacement = f'href={quote_char}{new_path}{remaining_path}{quote_char}'
                    else:
                        # Direct reference in quotes
                        remaining_path = match.group(1)
                        quote_char = '"' if pattern.startswith('"{') else "'"
                        replacement = f'{quote_char}{new_path}{remaining_path}{quote_char}'

                    old_match = match.group(0)
                    content = content[:match.start()] + \
                        replacement + content[match.end():]
                    changes_made.append(f"  {old_match} → {replacement}")

        # Write back if changes were made
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return changes_made

        return []

    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return []


def main():
    parser = argparse.ArgumentParser(
        description='Fix cross-references in documentation files')
    parser.add_argument('directory', help='Directory to process')
    parser.add_argument('--dry-run', action='store_true',
                        help='Show what would be changed without making changes')

    args = parser.parse_args()

    if not os.path.exists(args.directory):
        print(f"Directory {args.directory} does not exist")
        return 1

    mapping = create_reference_mapping()
    total_files_processed = 0
    total_files_changed = 0

    print(f"🔧 Processing files in {args.directory}")
    print(f"📋 Using {len(mapping)} reference mappings")

    if args.dry_run:
        print("🏃 DRY RUN MODE - No changes will be made")

    # Process all .md and .mdx files
    for root, dirs, files in os.walk(args.directory):
        for file in files:
            if file.endswith(('.md', '.mdx')):
                file_path = os.path.join(root, file)
                total_files_processed += 1

                if args.dry_run:
                    # For dry run, just check what would change
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()

                        found_references = []
                        for old_path in mapping.keys():
                            if old_path in content:
                                found_references.append(old_path)

                        if found_references:
                            print(f"\n📄 {file_path}")
                            print(
                                f"   Would update references: {', '.join(found_references)}")
                            total_files_changed += 1
                    except Exception as e:
                        print(f"Error reading {file_path}: {e}")
                else:
                    # Actually make changes
                    changes = fix_cross_references_in_file(file_path, mapping)
                    if changes:
                        total_files_changed += 1
                        print(f"\n✅ {file_path}")
                        for change in changes:
                            print(change)

    print(f"\n📊 Summary:")
    print(f"   Files processed: {total_files_processed}")
    print(
        f"   Files {'that would be ' if args.dry_run else ''}changed: {total_files_changed}")

    if args.dry_run:
        print(f"\n🚀 Run without --dry-run to apply changes")
    else:
        print(f"\n🎉 Cross-reference updates complete!")


if __name__ == '__main__':
    main()
