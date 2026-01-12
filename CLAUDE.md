# SaladCloud Documentation

Official documentation for SaladCloud at [docs.salad.com](https://docs.salad.com). Built with
[Mintlify](https://mintlify.com/).

## Tech Stack

- **Framework**: Mintlify (configured in `docs.json`)
- **Content**: MDX (Markdown with JSX components)
- **Formatting**: Prettier
- **Spell Check**: cspell (7 languages)
- **API Specs**: OpenAPI 3.0 in `api-specs/`

## Directory Structure

```
container-engine/     # Salad Container Engine (main product)
transcription/        # Transcription API
gateway-service/      # Residential IP proxy service
storage/              # S4 storage service
general/              # Account & general docs
api-specs/            # OpenAPI specifications
scripts/              # Automation scripts
```

Each product follows [Diátaxis](https://diataxis.fr/):

- `explanation/` - Conceptual docs (labeled "Products" in nav)
- `tutorials/` - Step-by-step learning guides
- `how-to-guides/` - Problem-oriented practical guides
- `reference/` - API docs, recipes, configuration

## Common Commands

```bash
npx -y mint dev                    # Start local dev server
npx prettier --write .             # Format all files
npx cspell "**/*.{md,mdx}"         # Check spelling
```

## File Conventions

- **Naming**: kebab-case with full words (e.g., `load-balancer-options.mdx` not `lb-opts.mdx`)
- **Images**: Place in sibling `images/` directory
- **Frontmatter**: Required for all MDX files:
  ```yaml
  ---
  title: 'Page Title'
  sidebarTitle: 'Sidebar Title'
  description: 'Meta description for SEO'
  ---
  ```
- **Date stamps**: Include `_Last Updated: Month Day, Year_` near top of content pages

## Navigation

All pages must be added to `docs.json` in the appropriate navigation section. The file is ~1,600 lines with:

- Tab definitions and groups
- 100+ URL redirects (add new ones when moving pages)
- Theme configuration

## Code Quality

All PRs must pass:

- Prettier formatting check
- cspell spell check
- OpenAPI validation
- Broken links detection
- docs.json structure validation

## MDX Components

Common Mintlify components:

```mdx
<CardGroup cols={2}>
  <Card title="Title" icon="icon-name" href="/path">
    Description
  </Card>
</CardGroup>

<Note>Important information</Note>
<Warning>Critical warning</Warning>
<Tip>Helpful tip</Tip>
```

## Automation Scripts

```bash
./scripts/add-recipe <spec-path>   # Generate recipe docs from OpenAPI
./scripts/add-all-endpoints        # Process all endpoint configs
python scripts/update-links.py     # Fix cross-references
python scripts/move-file.py        # Move files with reference updates
```

## Workflow Guidelines

1. **Before editing**: Read existing content to understand context
2. **Adding pages**: Update `docs.json` navigation
3. **Moving pages**: Add redirect in `docs.json`, update all references
4. **Images**: Use descriptive names, place in `images/` subdirectory
5. **Code examples**: Include language tags, test that examples work
6. **Links**: Use relative paths for internal links

## Custom Validation

Use the `/docs-validation` skill to validate tutorials and guides:

- Checks code block syntax (Python, Dockerfile, Bash, JSON, YAML)
- Validates API examples against OpenAPI specs
- Verifies portal UI instructions match actual interface
- Checks content freshness and terminology

## Key URLs

- **Production**: https://docs.salad.com
- **Portal**: https://portal.salad.com
- **API Base**: https://api.salad.com
- **Discord**: https://discord.gg/ApSm4Kn7Aq
