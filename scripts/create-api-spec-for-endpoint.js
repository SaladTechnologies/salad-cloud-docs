const fs = require('fs')
const path = require('path')
const { parse } = require('yaml')

const usage = `
Usage: node scripts/create-api-spec-for-endpoint.js <config-file>

This script creates an OpenAPI spec for an endpoint based on the base schema and input/output schemas provided in the config file.
The config file must be JSON formatted, and should have the following structure:
{
    "baseSchema": "path/to/base/schema",
    "inputSchema": "path/to/input/schema",
    "outputSchema": "path/to/output/schema",
    "endpointId": "endpoint-id",
    "endpointName": "Endpoint Name",
    "schemaName": "SchemaName",
    "apiDocPath": "path/to/api-docs"
}

A new schema file will be created in the same directory as the base schema, with the name <endpointId>.json.
`

// Directory being run from
const dir = process.cwd()

const getImportName = (filePath) => {
    return path.resolve(dir, filePath)
}

/**
 * Mintlify supports schemas in both JSON and YAML formats. This function
 * reads a file in either format and returns the parsed content.
 * @param {string} file A path to a JSON or YAML file
 * @returns
 */
function loadJSONorYAML(file) {
    const fileContent = fs.readFileSync(file, 'utf8')
    const isJson = file.endsWith('.json')
    return isJson ? JSON.parse(fileContent) : parse(fileContent)
}

/**
 * Deep clone an object using JSON serialization.
 * @param {any} obj Any JSON-serializable object
 * @returns
 */
const clone = (obj) => JSON.parse(JSON.stringify(obj))

if (process.argv.length !== 3) {
    console.error(usage)
    process.exit(1)
}
/**
 * The config file is the first argument passed to the script
 */
const configFile = getImportName(process.argv[2])

/**
 * We start with the base salad cloud schema, because our endpoint
 * is essentially a clone of the inference endpoints schemas, but with
 * the .input and .output schemas replaced with something custom.
 */
console.log(`Reading config file: ${configFile}`)
const config = require(configFile)

const schema = loadJSONorYAML(getImportName(config.baseSchema))
const inputSchema = loadJSONorYAML(getImportName(config.inputSchema))
const outputSchema = loadJSONorYAML(getImportName(config.outputSchema))

const { endpointId, endpointName, schemaName } = config
const inputSchemaName = `${schemaName}Input`
const outputSchemaName = `${schemaName}Output`
const jobSchemaName = `${schemaName}Job`

/**
 * Create a new schema object with the same structure as the base schema,
 * but with the title and description updated to reflect the new endpoint.
 */
const newSchema = clone(schema)
newSchema.info.title = endpointName
newSchema.info.description = `API for ${endpointName}`
newSchema.paths = {}

/**
 * Add the required new schemas to the components section
 */
// .input
newSchema.components.schemas[inputSchemaName] = inputSchema
newSchema.components.schemas[jobSchemaName] = clone(schema.components.schemas.InferenceEndpointJob)
newSchema.components.schemas[jobSchemaName].description = `Job input schema for ${endpointName}`
newSchema.components.schemas[jobSchemaName].properties.input = { $ref: `#/components/schemas/${inputSchemaName}` }

// .output
newSchema.components.schemas[outputSchemaName] = outputSchema
newSchema.components.schemas[jobSchemaName].properties.output = { $ref: `#/components/schemas/${outputSchemaName}` }

/**
 * Duplicate the CreateInferenceEndpointJob schema and update it with custom input and output
 */
newSchema.components.schemas[`Create${jobSchemaName}`] = clone(schema.components.schemas.CreateInferenceEndpointJob)
newSchema.components.schemas[`Create${jobSchemaName}`].description = `Create a job for ${endpointName}`
newSchema.components.schemas[`Create${jobSchemaName}`].properties.input = {
    $ref: `#/components/schemas/${inputSchemaName}`,
}

/**
 * Duplicate the InferenceEndpointJobList schema and update it with the new job schema
 */
newSchema.components.schemas[`${jobSchemaName}List`] = clone(schema.components.schemas.InferenceEndpointJobList)
newSchema.components.schemas[`${jobSchemaName}List`].description = `List of jobs for ${endpointName}`
newSchema.components.schemas[`${jobSchemaName}List`].properties.items = {
    $ref: `#/components/schemas/${jobSchemaName}`,
}

/**
 * The Request and Response body schemas are also defined in the components section.
 * As before, we duplicate the existing schemas and update them.
 */

/**
 * Request Body: Create
 */
newSchema.components.requestBodies[`Create${jobSchemaName}`] = clone(
    schema.components.requestBodies.CreateInferenceEndpointJob,
)
newSchema.components.requestBodies[`Create${jobSchemaName}`].content['application/json'].schema = {
    $ref: `#/components/schemas/Create${jobSchemaName}`,
}

/**
 * There are many irrelevant request bodies from the base schema that we can clear out.
 */
Object.keys(newSchema.components.requestBodies).forEach((key) => {
    if (key !== `Create${jobSchemaName}`) {
        delete newSchema.components.requestBodies[key]
    }
})

/**
 * Response Bodies
 */
// List
newSchema.components.responses[`List${jobSchemaName}`] = clone(schema.components.responses.ListInferenceEndpointJobs)
newSchema.components.responses[`List${jobSchemaName}`].content['application/json'].schema = {
    $ref: `#/components/schemas/${jobSchemaName}List`,
}

// Get
newSchema.components.responses[`Get${jobSchemaName}`] = clone(schema.components.responses.GetInferenceEndpointJob)
newSchema.components.responses[`Get${jobSchemaName}`].content['application/json'].schema = {
    $ref: `#/components/schemas/${jobSchemaName}`,
}

// Create
newSchema.components.responses[`Create${jobSchemaName}`] = clone(schema.components.responses.CreateInferenceEndpointJob)
newSchema.components.responses[`Create${jobSchemaName}`].content['application/json'].schema = {
    $ref: `#/components/schemas/${jobSchemaName}`,
}

/**
 * There are many irrelevant response bodies from the base schema that we can clear out.
 * We only need the errors, and the job-related responses.
 */
function isNumber(str) {
    return !isNaN(str) && !isNaN(parseFloat(str))
}
Object.keys(newSchema.components.responses).forEach((key) => {
    if (
        ![`List${jobSchemaName}`, `Get${jobSchemaName}`, `Create${jobSchemaName}`, 'UnknownError'].includes(key) &&
        !isNumber(key) &&
        !key.includes('InferenceEndpoint')
    ) {
        delete newSchema.components.responses[key]
    }
})

// Path Parameters
newSchema.components.parameters.job_id = clone(schema.components.parameters.inference_endpoint_job_id)
newSchema.components.parameters.job_id.description = `The ID of the job for ${endpointName}`
newSchema.components.parameters.job_id.name = 'job_id'

/**
 * Now we add the new endpoint to the paths section of the schema.
 */
// Resource: /organizations/{organization_name}/inference-endpoints/{inference_endpoint_name}
const endpointPath = `/organizations/{organization_name}/inference-endpoints/${endpointId}`
newSchema.paths[endpointPath] = clone(
    schema.paths['/organizations/{organization_name}/inference-endpoints/{inference_endpoint_name}'],
)

// Remove the no-longer-needed variable reference
let inferenceEndpointNameParamIndex = newSchema.paths[endpointPath].parameters.findIndex(
    (param) => param.$ref === '#/components/parameters/inference_endpoint_name',
)
if (inferenceEndpointNameParamIndex !== -1) {
    newSchema.paths[endpointPath].parameters.splice(inferenceEndpointNameParamIndex, 1)
}
// Resource: /organizations/{organization_name}/inference-endpoints/{inference_endpoint_name}/jobs
newSchema.paths[`${endpointPath}/jobs`] = clone(
    schema.paths['/organizations/{organization_name}/inference-endpoints/{inference_endpoint_name}/jobs'],
)
newSchema.paths[`${endpointPath}/jobs`].summary = `Jobs for ${endpointName}`
newSchema.paths[`${endpointPath}/jobs`].description = `Operations for ${endpointName} jobs`

// Remove the no-longer-needed variable reference
const jobsInferenceEndpointNameParamIndex = newSchema.paths[`${endpointPath}/jobs`].parameters.findIndex(
    (param) => param.$ref === '#/components/parameters/inference_endpoint_name',
)
if (jobsInferenceEndpointNameParamIndex !== -1) {
    newSchema.paths[`${endpointPath}/jobs`].parameters.splice(jobsInferenceEndpointNameParamIndex, 1)
}

newSchema.paths[`${endpointPath}/jobs`].get.summary = `List jobs for ${endpointName}`
newSchema.paths[`${endpointPath}/jobs`].get.description = `Retrieves a list of jobs for ${endpointName}`
newSchema.paths[`${endpointPath}/jobs`].get.responses['200'] = {
    $ref: `#/components/responses/List${jobSchemaName}`,
}
newSchema.paths[`${endpointPath}/jobs`].post.summary = `Create a job for ${endpointName}`
newSchema.paths[`${endpointPath}/jobs`].post.description = `Creates a job for ${endpointName}`
newSchema.paths[`${endpointPath}/jobs`].post.requestBody = {
    $ref: `#/components/requestBodies/Create${jobSchemaName}`,
}
newSchema.paths[`${endpointPath}/jobs`].post.responses['201'] = {
    $ref: `#/components/responses/Create${jobSchemaName}`,
}

// Resource: /organizations/{organization_name}/inference-endpoints/{inference_endpoint_name}/jobs/{job_id}
newSchema.paths[`${endpointPath}/jobs/{job_id}`] = clone(
    schema.paths[
        '/organizations/{organization_name}/inference-endpoints/{inference_endpoint_name}/jobs/{inference_endpoint_job_id}'
    ],
)
newSchema.paths[`${endpointPath}/jobs/{job_id}`].summary = `Job for ${endpointName}`
newSchema.paths[`${endpointPath}/jobs/{job_id}`].description = `Operations for a ${endpointName} job`
newSchema.paths[`${endpointPath}/jobs/{job_id}`].parameters.push({ $ref: '#/components/parameters/job_id' })

// Remove the no-longer-needed variable reference
const jobInferenceEndpointNameParamIndex = newSchema.paths[`${endpointPath}/jobs/{job_id}`].parameters.findIndex(
    (param) => param.$ref === '#/components/parameters/inference_endpoint_name',
)
if (jobInferenceEndpointNameParamIndex !== -1) {
    newSchema.paths[`${endpointPath}/jobs/{job_id}`].parameters.splice(jobInferenceEndpointNameParamIndex, 1)
}
inferenceEndpointNameParamIndex = newSchema.paths[`${endpointPath}/jobs/{job_id}`].parameters.findIndex(
    (param) => param.$ref === '#/components/parameters/inference_endpoint_job_id',
)
if (inferenceEndpointNameParamIndex !== -1) {
    newSchema.paths[`${endpointPath}/jobs/{job_id}`].parameters.splice(inferenceEndpointNameParamIndex, 1)
}

newSchema.paths[`${endpointPath}/jobs/{job_id}`].get.summary = `Get job for ${endpointName}`
newSchema.paths[`${endpointPath}/jobs/{job_id}`].get.description = `Retrieves a job for ${endpointName}`
newSchema.paths[`${endpointPath}/jobs/{job_id}`].get.responses['200'] = {
    $ref: `#/components/responses/Get${jobSchemaName}`,
}

newSchema.paths[`${endpointPath}/jobs/{job_id}`].delete.summary = `Delete job for ${endpointName}`

/**
 * Write the new schema to a file
 */
const newSchemaPath = path.join(path.dirname(config.baseSchema), `${endpointId}.json`)
fs.writeFileSync(newSchemaPath, JSON.stringify(newSchema, null, 2))

console.log(`New schema created: ${newSchemaPath}`)
