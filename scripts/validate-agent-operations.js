#!/usr/bin/env node

const fs = require('fs')
const path = require('path')
const YAML = require('yaml')

const root = path.resolve(__dirname, '..')
const runbooks = [
    'agents/overview.mdx',
    'agents/container-engine/discover-scope-and-preflight.mdx',
    'agents/container-engine/deploy-or-update-container-group.mdx',
    'agents/container-engine/monitor-and-operate-container-group.mdx',
    'agents/container-engine/troubleshoot-container-group.mdx',
    'agents/container-engine/configure-job-queue-autoscaling.mdx',
    'agents/reference/safety-retries-and-freshness.mdx',
]
const skills = [
    'salad-container-engine-preflight',
    'salad-container-engine-deploy',
    'salad-container-engine-operate',
    'salad-container-engine-troubleshoot',
    'salad-job-queue-autoscaling',
]
const contract = [
    'When to use this runbook',
    'When not to use it',
    'Required inputs',
    'Authoritative sources',
    'Dynamic values to retrieve',
    'Preflight checks',
    'Procedure',
    'Decision rules',
    'Expected states and responses',
    'Retry behavior',
    'Verification',
    'Rollback or recovery',
    'Stop and escalation conditions',
    'Evidence to return to the user',
]
const errors = []

function read(relativePath) {
    const absolutePath = path.join(root, relativePath)
    if (!fs.existsSync(absolutePath)) {
        errors.push(`Missing file: ${relativePath}`)
        return ''
    }
    return fs.readFileSync(absolutePath, 'utf8')
}

function parseFrontmatter(relativePath, content) {
    const match = content.match(/^---\n([\s\S]*?)\n---\n/)
    if (!match) {
        errors.push(`Missing YAML frontmatter: ${relativePath}`)
        return {}
    }
    try {
        return YAML.parse(match[1])
    } catch (error) {
        errors.push(`Invalid YAML frontmatter in ${relativePath}: ${error.message}`)
        return {}
    }
}

function collectOperations(specPath) {
    const spec = YAML.parse(read(specPath))
    const operations = new Set()
    for (const pathItem of Object.values(spec.paths || {})) {
        for (const method of ['get', 'post', 'put', 'patch', 'delete']) {
            if (pathItem[method]?.operationId) operations.add(pathItem[method].operationId)
        }
    }
    return operations
}

function collectSchemaFields(specPath) {
    const spec = YAML.parse(read(specPath))
    const fields = new Set()
    for (const schema of Object.values(spec.components?.schemas || {})) {
        for (const field of Object.keys(schema.properties || {})) fields.add(field)
    }
    return fields
}

const operationIds = new Set([
    ...collectOperations('api-specs/salad-cloud.yaml'),
    ...collectOperations('api-specs/salad-cloud-imds.yaml'),
])
const schemaFields = new Set([
    ...collectSchemaFields('api-specs/salad-cloud.yaml'),
    ...collectSchemaFields('api-specs/salad-cloud-imds.yaml'),
])

function validateInternalLinks(relativePath, content) {
    for (const match of content.matchAll(/\[[^\]]*\]\((\/[^)#?]+)(?:#[^)]+)?\)/g)) {
        const target = match[1].replace(/^\//, '')
        const candidates = [target, `${target}.mdx`, `${target}.md`]
        if (!candidates.some((candidate) => fs.existsSync(path.join(root, candidate)))) {
            errors.push(`Unresolved internal link in ${relativePath}: ${match[1]}`)
        }
    }
}

function validateJsonFences(relativePath, content) {
    for (const match of content.matchAll(/```json\n([\s\S]*?)\n```/g)) {
        try {
            JSON.parse(match[1])
        } catch (error) {
            errors.push(`Invalid JSON fence in ${relativePath}: ${error.message}`)
        }
    }
}

function validateShellJson(relativePath, content) {
    for (const fence of content.matchAll(/```(?:bash|shell)\n([\s\S]*?)\n```/g)) {
        for (const match of fence[1].matchAll(/--data\s+'([\s\S]*?)'(?:\s|$)/g)) {
            try {
                JSON.parse(match[1])
            } catch (error) {
                errors.push(`Invalid JSON passed to --data in ${relativePath}: ${error.message}`)
            }
        }
    }
}

function validateOperationMentions(relativePath, content) {
    const operationLists = content.matchAll(/Operation(?: ID)?s?:\s*((?:`[a-z][a-z0-9_]+`(?:\s*(?:,|and)\s*)?)+)/gi)
    for (const operationList of operationLists) {
        for (const match of operationList[1].matchAll(/`([a-z][a-z0-9_]+)`/g)) {
            if (!operationIds.has(match[1])) errors.push(`Unknown operation ID in ${relativePath}: ${match[1]}`)
        }
    }
    const operationLikeTokens = content.matchAll(
        /`((?:get|list|create|update|delete|start|stop|query|reallocate|recreate|restart|replace)_[a-z0-9_]+)`/g,
    )
    for (const match of operationLikeTokens) {
        if (!schemaFields.has(match[1]) && !operationIds.has(match[1])) {
            errors.push(`Unknown operation-like token in ${relativePath}: ${match[1]}`)
        }
    }
}

for (const relativePath of runbooks) {
    const content = read(relativePath)
    const frontmatter = parseFrontmatter(relativePath, content)
    for (const field of ['title', 'sidebarTitle', 'description']) {
        if (!frontmatter[field]) errors.push(`Missing ${field} frontmatter in ${relativePath}`)
    }
    if (/^hidden:\s*true$/m.test(content)) errors.push(`Runbook must not use hidden: true: ${relativePath}`)
    for (const heading of contract) {
        if (!content.includes(`## ${heading}`)) errors.push(`Missing runbook section in ${relativePath}: ${heading}`)
    }
    validateInternalLinks(relativePath, content)
    validateJsonFences(relativePath, content)
    validateShellJson(relativePath, content)
    validateOperationMentions(relativePath, content)
}

for (const skill of skills) {
    const relativePath = `.mintlify/skills/${skill}/SKILL.md`
    const content = read(relativePath)
    const frontmatter = parseFrontmatter(relativePath, content)
    if (frontmatter.name !== skill) errors.push(`Skill name must match directory: ${relativePath}`)
    if (!frontmatter.description) errors.push(`Missing skill description: ${relativePath}`)
    if (frontmatter.license !== 'CC-BY-4.0') errors.push(`Unexpected skill license: ${relativePath}`)
    validateInternalLinks(relativePath, content)
    validateOperationMentions(relativePath, content)
}

const docs = JSON.parse(read('docs.json'))
const agentTab = docs.navigation?.tabs?.find((tab) => tab.tab === 'Agent Operations')
if (!agentTab || agentTab.hidden !== true || agentTab.searchable !== true) {
    errors.push('Agent Operations tab must be hidden and searchable')
} else {
    const configuredPages = agentTab.groups.flatMap((group) => group.pages || [])
    if (JSON.stringify(configuredPages) !== JSON.stringify(runbooks.map((page) => page.replace(/\.mdx$/, '')))) {
        errors.push('Agent Operations tab must contain every runbook exactly once and in the expected order')
    }
}
if (!docs.markdown?.instructions) errors.push('docs.json must define markdown.instructions')
if (docs.markdown?.instructions?.trim().split(/\s+/).length > 150) {
    errors.push('docs.json markdown.instructions must stay at or below 150 words')
}

const mintignore = read('.mintignore')
if (!mintignore.split('\n').includes('agent-evals/')) errors.push('.mintignore must exclude agent-evals/')

let scenarios
try {
    scenarios = YAML.parse(read('agent-evals/scenarios.yaml'))?.scenarios
} catch (error) {
    errors.push(`Invalid agent-evals/scenarios.yaml: ${error.message}`)
}
const scenarioFields = [
    'id',
    'prompt',
    'expected_skill',
    'required_sources',
    'required_operations',
    'required_dynamic_checks',
    'required_safety_behavior',
    'forbidden_assumptions',
    'success_criteria',
]
if (!Array.isArray(scenarios) || scenarios.length < 8) {
    errors.push('agent-evals/scenarios.yaml must contain at least eight scenarios')
} else {
    const ids = new Set()
    for (const scenario of scenarios) {
        for (const field of scenarioFields) {
            if (scenario[field] === undefined || scenario[field] === null) {
                errors.push(`Scenario ${scenario.id || '<unknown>'} is missing ${field}`)
            }
        }
        for (const field of scenarioFields.slice(3)) {
            if (!Array.isArray(scenario[field]) || scenario[field].length === 0) {
                errors.push(`Scenario ${scenario.id || '<unknown>'} must have a non-empty ${field} list`)
            }
        }
        if (ids.has(scenario.id)) errors.push(`Duplicate scenario ID: ${scenario.id}`)
        ids.add(scenario.id)
        if (!skills.includes(scenario.expected_skill)) {
            errors.push(`Unknown expected skill in ${scenario.id}: ${scenario.expected_skill}`)
        }
        for (const source of scenario.required_sources || []) read(source)
        for (const operation of scenario.required_operations || []) {
            if (!operationIds.has(operation)) errors.push(`Unknown operation ID in ${scenario.id}: ${operation}`)
        }
    }
}

if (errors.length) {
    console.error(`Agent operations validation failed with ${errors.length} error(s):`)
    for (const error of errors) console.error(`- ${error}`)
    process.exit(1)
}

console.log(
    `Agent operations validation passed: ${runbooks.length} runbooks, ${skills.length} skills, ${scenarios.length} scenarios, and ${operationIds.size} OpenAPI operation IDs checked.`,
)
