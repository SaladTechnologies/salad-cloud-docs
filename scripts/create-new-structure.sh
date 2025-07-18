#!/bin/bash

# Script to create the new DiATaxis-based directory structure for SaladCloud docs
# This creates the directories but does not move any files yet

set -e

echo "Creating new DiATaxis directory structure..."

# Get the root directory (assuming script is run from the repo root or scripts folder)
if [ -d "scripts" ]; then
  ROOT_DIR="."
else
  ROOT_DIR=".."
fi

cd "$ROOT_DIR"

# Create Container Engine structure
echo "Creating Container Engine directories..."
mkdir -p container-engine/{tutorials,how-to-guides,explanation,reference,images}

# Create Transcription structure
echo "Creating Transcription directories..."
mkdir -p transcription/{tutorials,how-to-guides,explanation,reference,images}

# Create Gateway Service structure
echo "Creating Gateway Service directories..."
mkdir -p gateway-service/{tutorials,how-to-guides,explanation,reference,images}

# Create Storage structure
echo "Creating Storage directories..."
mkdir -p storage/{tutorials,how-to-guides,explanation,reference,images}

# Create support structure (if it doesn't exist)
echo "Creating Support directories..."
mkdir -p support/images

# Ensure shared resources exist
echo "Creating shared resource directories..."
mkdir -p shared/images
mkdir -p site-scripts

# Create placeholder README files in each main directory to explain the structure
echo "Creating README files to document the structure..."

cat >container-engine/README.md <<'EOF'
# Container Engine Documentation

This directory contains all documentation for SaladCloud Container Engine (SCE), organized using the DiATaxis methodology.

## Structure

- **tutorials/**: Learning-oriented content (quickstarts, getting started guides)
- **how-to-guides/**: Problem-oriented content (deployment guides, specific use cases)
- **explanation/**: Understanding-oriented content (concepts, architecture, billing)
- **reference/**: Information-oriented content (API docs, configuration options, FAQs)
- **images/**: All images and media for Container Engine documentation

## DiATaxis Categories

### Tutorials
Step-by-step learning experiences for new users:
- Getting started with SCE
- Your first container deployment
- Recipe quickstarts

### How-to Guides
Solution-focused guides for specific problems:
- Deploying specific applications (LLMs, image generation, etc.)
- Integration guides (Kubernetes, logging, registries)
- Configuration examples

### Explanation
Conceptual understanding of SCE:
- Architecture overviews
- Container groups concepts
- Billing and pricing explanations
- Feature explanations

### Reference
Technical specifications and lookup information:
- API documentation
- Configuration options
- Command references
- FAQs
EOF

cat >transcription/README.md <<'EOF'
# Transcription API Documentation

This directory contains all documentation for SaladCloud Transcription API, organized using the DiATaxis methodology.

## Structure

- **tutorials/**: Learning-oriented content
- **how-to-guides/**: Problem-oriented content
- **explanation/**: Understanding-oriented content
- **reference/**: Information-oriented content
- **images/**: All images and media for Transcription documentation
EOF

cat >gateway-service/README.md <<'EOF'
# Gateway Service Documentation

This directory contains all documentation for SaladCloud Gateway Service (SGS), organized using the DiATaxis methodology.

## Structure

- **tutorials/**: Learning-oriented content
- **how-to-guides/**: Problem-oriented content
- **explanation/**: Understanding-oriented content
- **reference/**: Information-oriented content
- **images/**: All images and media for Gateway Service documentation
EOF

cat >storage/README.md <<'EOF'
# Storage (S4) Documentation

This directory contains all documentation for SaladCloud Simple Storage Service (S4), organized using the DiATaxis methodology.

## Structure

- **tutorials/**: Learning-oriented content
- **how-to-guides/**: Problem-oriented content
- **explanation/**: Understanding-oriented content
- **reference/**: Information-oriented content
- **images/**: All images and media for Storage documentation
EOF

# Create .gitkeep files to ensure empty directories are tracked
echo "Creating .gitkeep files for empty directories..."
find container-engine transcription gateway-service storage -type d -empty -exec touch {}/.gitkeep \;

echo ""
echo "✅ New directory structure created successfully!"
echo ""
echo "📁 Directory structure:"
echo "├── container-engine/"
echo "│   ├── tutorials/"
echo "│   ├── how-to-guides/"
echo "│   ├── explanation/"
echo "│   ├── reference/"
echo "│   └── images/"
echo "├── transcription/"
echo "│   ├── tutorials/"
echo "│   ├── how-to-guides/"
echo "│   ├── explanation/"
echo "│   ├── reference/"
echo "│   └── images/"
echo "├── gateway-service/"
echo "│   ├── tutorials/"
echo "│   ├── how-to-guides/"
echo "│   ├── explanation/"
echo "│   ├── reference/"
echo "│   └── images/"
echo "└── storage/"
echo "    ├── tutorials/"
echo "    ├── how-to-guides/"
echo "    ├── explanation/"
echo "    ├── reference/"
echo "    └── images/"
echo ""
echo "📝 Next steps:"
echo "1. Review the README.md files in each product directory"
echo "2. Plan the content migration using the DiATaxis classification"
echo "3. Update docs.json with the new navigation structure"
echo "4. Create migration scripts for moving existing content"
