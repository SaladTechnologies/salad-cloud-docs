# Repository guidance for coding agents

Read `CLAUDE.md` before changing this repository. Follow the existing Mintlify, MDX, Diátaxis, frontmatter, kebab-case,
and last-updated conventions. The OpenAPI specifications in `api-specs/` are authoritative for API paths, operation IDs,
schemas, required fields, and enums.

Use the repository's supported checks:

- `npx prettier "./**/*.{md,mdx}" --check`
- `npx cspell "**/*.{md,mdx}"`
- `python3 .github/scripts/validate_docs_json.py`
- `.github/scripts/validate-all-workflows.sh`
- `npx -y mint validate`
- `npx --yes mintlify broken-links`
- `npm run validate:agent-operations`
- `npx -y mint dev` for local preview

Validate every changed link and example. Keep diffs focused and do not rewrite unrelated content. A documentation change
is done only when its navigation, formatting, spelling, links, examples, schemas, and rendered behavior are verified, or
an unavailable check is reported precisely. See `.claude/skills/docs-validation/SKILL.md` for walkthrough guidance.
