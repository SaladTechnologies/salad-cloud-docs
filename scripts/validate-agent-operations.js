#!/usr/bin/env node

// cspell:ignore evals

const fs = require('fs')
const path = require('path')
const childProcess = require('child_process')
const YAML = require('yaml')

const root = path.resolve(__dirname, '..')
const runbooks = [
    'agents/overview.mdx',
    'agents/container-engine/discover-scope-and-preflight.mdx',
    'agents/container-engine/deploy-or-update-container-group.mdx',
    'agents/container-engine/monitor-and-operate-container-group.mdx',
    'agents/container-engine/troubleshoot-container-group.mdx',
    'agents/container-engine/configure-job-queue-autoscaling.mdx',
    'agents/ai-gateway/select-model-and-send-request.mdx',
    'agents/ai-gateway/troubleshoot-request.mdx',
    'agents/transcription/choose-api-and-preflight.mdx',
    'agents/transcription/submit-and-monitor-job.mdx',
    'agents/transcription-lite/submit-and-monitor-job.mdx',
    'agents/transcription/troubleshoot-job.mdx',
    'agents/reference/safety-retries-and-freshness.mdx',
]
const skills = [
    'salad-container-engine-preflight',
    'salad-container-engine-deploy',
    'salad-container-engine-operate',
    'salad-container-engine-troubleshoot',
    'salad-job-queue-autoscaling',
    'salad-ai-gateway-request',
    'salad-ai-gateway-troubleshoot',
    'salad-transcription-preflight',
    'salad-transcription-job',
    'salad-transcription-lite-job',
    'salad-transcription-troubleshoot',
]
const transcriptionExamplePages = [
    'transcription/tutorials/transcription-quick-start.mdx',
    'transcription/how-to-guides/speech-to-text.mdx',
    'transcription/how-to-guides/features/translation.mdx',
    'transcription/how-to-guides/features/llm-features.mdx',
]
const specPaths = [
    'api-specs/salad-cloud.yaml',
    'api-specs/salad-cloud-imds.yaml',
    'api-specs/transcribe.json',
    'api-specs/transcription-lite.json',
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

const specsByPath = new Map(specPaths.map((specPath) => [specPath, YAML.parse(read(specPath))]))
const operationsBySpec = new Map(specPaths.map((specPath) => [specPath, collectOperations(specPath)]))
const operationIds = new Set([...operationsBySpec.values()].flatMap((operations) => [...operations]))
const schemaFields = new Set(specPaths.flatMap((specPath) => [...collectSchemaFields(specPath)]))
const aiGatewayEndpoints = new Set(['GET /v1/models', 'POST /v1/chat/completions'])

function validateTranscriptionProductSchemas() {
    const primary = specsByPath.get('api-specs/transcribe.json')?.components?.schemas
    const lite = specsByPath.get('api-specs/transcription-lite.json')?.components?.schemas
    const primaryInput = primary?.SaladCloudTranscriptionAPIInput
    const liteInput = lite?.SaladCloudTranscriptionLiteAPIInput
    const primaryOutput = primary?.SaladCloudTranscriptionAPIOutput
    const expectedPrimaryInput = {
        url: { type: 'string' },
        language_code: { type: 'string', nullable: true, default: null },
        audio_stream_index: { type: 'integer', nullable: true, default: null },
        multichannel: { type: 'boolean', default: false },
        return_as_file: { type: 'boolean', default: false },
        word_level_timestamps: { type: 'boolean', default: false },
        sentence_level_timestamps: { type: 'boolean', default: false },
        diarization: { type: 'boolean', default: false },
        sentence_diarization: { type: 'boolean', default: false },
        srt: { type: 'boolean', default: false },
        translate: { type: 'string', nullable: true, default: null },
        llm_translation: { type: 'string', nullable: true, default: null },
        srt_translation: { type: 'string', nullable: true, default: null },
        custom_prompt: { type: 'string', nullable: true, default: null },
        custom_vocabulary: { type: 'string', nullable: true, default: null },
        summarize: { type: 'number', nullable: true, default: null, minimum: 0, maximum: 2000 },
        overall_classification: { type: 'boolean', default: false },
        classification_labels: { type: 'string', nullable: true, default: null },
        overall_sentiment_analysis: { type: 'boolean', default: false },
        enhanced_accuracy: { type: 'boolean', default: false },
    }

    if (JSON.stringify(primaryInput?.required) !== JSON.stringify(['url'])) {
        errors.push('Primary Transcription input must require only url')
    }
    const actualFields = Object.keys(primaryInput?.properties || {}).sort()
    const expectedFields = Object.keys(expectedPrimaryInput).sort()
    if (JSON.stringify(actualFields) !== JSON.stringify(expectedFields)) {
        errors.push('Primary Transcription input fields do not match the current documented contract')
    }
    for (const [field, expected] of Object.entries(expectedPrimaryInput)) {
        const actual = primaryInput?.properties?.[field]
        if (!actual) {
            errors.push(`Primary Transcription input is missing ${field}`)
            continue
        }
        for (const [attribute, value] of Object.entries(expected)) {
            if (actual[attribute] !== value) {
                errors.push(`Primary Transcription ${field}.${attribute} must be ${JSON.stringify(value)}`)
            }
        }
    }
    for (const field of ['audio_stream_index', 'multichannel', 'enhanced_accuracy']) {
        if (liteInput?.properties?.[field])
            errors.push(`Transcription Lite must not define primary-only field ${field}`)
    }
    const supportedTranslations = ['english', 'french', 'german', 'italian', 'portuguese', 'hindi', 'spanish', 'thai']
    for (const field of ['llm_translation', 'srt_translation']) {
        const description = primaryInput?.properties?.[field]?.description?.toLowerCase() || ''
        for (const language of supportedTranslations) {
            if (!description.includes(language)) {
                errors.push(`Primary Transcription ${field} description is missing supported language ${language}`)
            }
        }
    }
    if (!primaryInput?.properties?.translate?.description?.includes('to_eng')) {
        errors.push('Primary Transcription translate description must identify to_eng as the defined behavior')
    }
    for (const field of [
        'word_segments',
        'sentence_level_timestamps',
        'timestamp_source',
        'srt_content',
        'summary',
        'llm_translation',
        'srt_translation',
        'llm_custom_vocabulary',
        'llm_result',
        'overall_classification',
        'overall_sentiment',
    ]) {
        if (!primaryOutput?.properties?.[field]) errors.push(`Primary Transcription output is missing ${field}`)
    }
}

validateTranscriptionProductSchemas()

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

function validateCompleteJsonFences(relativePath, content) {
    for (const match of content.matchAll(/```json\n([\s\S]*?)\n```/g)) {
        const example = match[1].trim()
        if (!example.startsWith('{') && !example.startsWith('[')) continue
        try {
            JSON.parse(example)
        } catch (error) {
            errors.push(`Invalid complete JSON example in ${relativePath}: ${error.message}`)
        }
    }
}

function resolveSchema(spec, schema) {
    if (!schema?.$ref) return schema
    const prefix = '#/components/schemas/'
    if (!schema.$ref.startsWith(prefix)) return schema
    return spec.components?.schemas?.[schema.$ref.slice(prefix.length)]
}

function validateSchemaValue(relativePath, value, schema, spec, location) {
    schema = resolveSchema(spec, schema)
    if (!schema) {
        errors.push(`Missing schema for ${location} in ${relativePath}`)
        return
    }
    if (value === null && schema.nullable) return

    const typeMatches =
        !schema.type ||
        (schema.type === 'object' && value !== null && typeof value === 'object' && !Array.isArray(value)) ||
        (schema.type === 'array' && Array.isArray(value)) ||
        (schema.type === 'string' && typeof value === 'string') ||
        (schema.type === 'boolean' && typeof value === 'boolean') ||
        (schema.type === 'number' && typeof value === 'number') ||
        (schema.type === 'integer' && Number.isInteger(value))
    if (!typeMatches) {
        errors.push(`Schema type mismatch at ${location} in ${relativePath}: expected ${schema.type}`)
        return
    }

    if (schema.enum && !schema.enum.includes(value)) {
        errors.push(`Value outside schema enum at ${location} in ${relativePath}: ${JSON.stringify(value)}`)
    }
    if (typeof value === 'number') {
        if (schema.minimum !== undefined && value < schema.minimum) {
            errors.push(`Value below schema minimum at ${location} in ${relativePath}: ${value}`)
        }
        if (schema.maximum !== undefined && value > schema.maximum) {
            errors.push(`Value above schema maximum at ${location} in ${relativePath}: ${value}`)
        }
    }

    if (schema.type === 'object') {
        const keys = Object.keys(value)
        if (schema.maxProperties !== undefined && keys.length > schema.maxProperties) {
            errors.push(`Too many properties at ${location} in ${relativePath}`)
        }
        for (const required of schema.required || []) {
            if (!(required in value))
                errors.push(`Missing required property ${location}.${required} in ${relativePath}`)
        }
        for (const key of keys) {
            if (schema.properties?.[key]) {
                validateSchemaValue(relativePath, value[key], schema.properties[key], spec, `${location}.${key}`)
            } else if (schema.additionalProperties === false) {
                errors.push(`Property absent from schema at ${location}.${key} in ${relativePath}`)
            }
        }
    }

    if (schema.type === 'array') {
        for (const [index, item] of value.entries()) {
            validateSchemaValue(relativePath, item, schema.items, spec, `${location}[${index}]`)
        }
    }
}

function validateShellJson(relativePath, content) {
    for (const fence of content.matchAll(/```(?:bash|shell)\n([\s\S]*?)\n```/g)) {
        const syntax = childProcess.spawnSync('bash', ['-n', '-c', fence[1]], { encoding: 'utf8', timeout: 2000 })
        if (syntax.status !== 0) {
            errors.push(`Invalid shell fence in ${relativePath}: ${syntax.error?.message || syntax.stderr.trim()}`)
        }
        for (const match of fence[1].matchAll(/--data\s+'([\s\S]*?)'(?:\s|$)/g)) {
            try {
                const body = JSON.parse(match[1])
                const requestSchema = [
                    {
                        marker: '/inference-endpoints/transcription-lite/jobs',
                        specPath: 'api-specs/transcription-lite.json',
                        schema: 'CreateSaladCloudTranscriptionLiteAPIJob',
                    },
                    {
                        marker: '/inference-endpoints/transcribe/jobs',
                        specPath: 'api-specs/transcribe.json',
                        schema: 'CreateSaladCloudTranscriptionAPIJob',
                    },
                ].find(({ marker }) => fence[1].includes(marker))
                if (requestSchema && fence[1].includes('--request POST')) {
                    const spec = specsByPath.get(requestSchema.specPath)
                    validateSchemaValue(
                        relativePath,
                        body,
                        spec.components.schemas[requestSchema.schema],
                        spec,
                        'request body',
                    )
                }
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

for (const relativePath of transcriptionExamplePages) {
    const content = read(relativePath)
    validateCompleteJsonFences(relativePath, content)
    validateInternalLinks(relativePath, content)
    if (relativePath.endsWith('transcription-quick-start.mdx')) validateShellJson(relativePath, content)
}

for (const skill of skills) {
    const relativePath = `.mintlify/skills/${skill}/SKILL.md`
    const content = read(relativePath)
    const frontmatter = parseFrontmatter(relativePath, content)
    if (frontmatter.name !== skill) errors.push(`Skill name must match directory: ${relativePath}`)
    if (!frontmatter.description) errors.push(`Missing skill description: ${relativePath}`)
    if (frontmatter.license !== 'CC-BY-4.0') errors.push(`Unexpected skill license: ${relativePath}`)
    for (const [rule, pattern] of [
        ['live/current data', /\b(live|current)\b/i],
        ['safety/stop behavior', /\b(never|stop|do not)\b/i],
        ['retry behavior', /\b(?:retry|retries|retried|retrying)\b/i],
        ['verification behavior', /\b(success|verify|verification)\b/i],
        ['escalation behavior', /\bescalat(?:e|es|ed|ing|ion)\b/i],
    ]) {
        if (!pattern.test(content)) errors.push(`Skill is missing ${rule}: ${relativePath}`)
    }
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
        const isAiGatewayScenario = scenario.expected_skill?.startsWith('salad-ai-gateway-')
        for (const field of scenarioFields) {
            if (scenario[field] === undefined || scenario[field] === null) {
                errors.push(`Scenario ${scenario.id || '<unknown>'} is missing ${field}`)
            }
        }
        for (const field of scenarioFields.slice(3)) {
            if (field === 'required_operations' && isAiGatewayScenario) {
                if (!Array.isArray(scenario[field])) {
                    errors.push(`Scenario ${scenario.id || '<unknown>'} must define ${field} as a list`)
                }
                continue
            }
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
        const requiredSpecs = (scenario.required_sources || []).filter((source) => source.startsWith('api-specs/'))
        if (isAiGatewayScenario) {
            if (!Array.isArray(scenario.required_endpoints) || scenario.required_endpoints.length === 0) {
                errors.push(`AI Gateway scenario ${scenario.id} must name at least one required endpoint`)
            }
            for (const endpoint of scenario.required_endpoints || []) {
                if (!aiGatewayEndpoints.has(endpoint)) {
                    errors.push(`Unknown AI Gateway endpoint in ${scenario.id}: ${endpoint}`)
                }
            }
            if ((scenario.required_operations || []).length !== 0) {
                errors.push(`AI Gateway scenario ${scenario.id} must not invent OpenAPI operation IDs`)
            }
            continue
        }
        if (requiredSpecs.length === 0) errors.push(`Scenario ${scenario.id} must name at least one API specification`)
        const scenarioOperations = new Set(
            requiredSpecs.flatMap((specPath) => [...(operationsBySpec.get(specPath) || [])]),
        )
        for (const operation of scenario.required_operations || []) {
            if (!operationIds.has(operation)) errors.push(`Unknown operation ID in ${scenario.id}: ${operation}`)
            if (!scenarioOperations.has(operation)) {
                errors.push(`Operation ID ${operation} is absent from the required specs for ${scenario.id}`)
            }
        }
    }
}

if (errors.length) {
    console.error(`Agent operations validation failed with ${errors.length} error(s):`)
    for (const error of errors) console.error(`- ${error}`)
    process.exit(1)
}

console.log(
    `Agent operations validation passed: ${runbooks.length} runbooks, ${skills.length} skills, ${scenarios.length} scenarios, and ${operationIds.size} unique operation IDs across ${specPaths.length} OpenAPI specifications checked.`,
)
