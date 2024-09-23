const fs = require('fs')
const { get } = require('http')
const path = require('path')

// Directory being run from
const dir = process.cwd()

const getImportName = (filePath) => {
    return path.resolve(dir, filePath)
}

const configFile = getImportName(process.argv[2])
console.log(`Reading config file: ${configFile}`)
const config = require(configFile)

/**
 * Update these values to match the new endpoint
 */

const schema = require(getImportName(config.baseSchema))
const inputSchema = require(getImportName(config.inputSchema))
const outputSchema = require(getImportName(config.outputSchema))

const { endpointId, endpointName, schemaName } = config
const inputSchemaName = `${schemaName}Input`
const outputSchemaName = `${schemaName}Output`
const jobSchemaName = `${schemaName}Job`

const clone = (obj) => JSON.parse(JSON.stringify(obj))

// .input
schema.components.schemas[inputSchemaName] = inputSchema
schema.components.schemas[jobSchemaName] = clone(schema.components.schemas.InferenceEndpointJob)
schema.components.schemas[jobSchemaName].description = `Job input schema for ${endpointName}`
schema.components.schemas[jobSchemaName].properties.input = { $ref: `#/components/schemas/${inputSchemaName}` }

// .output
schema.components.schemas[outputSchemaName] = outputSchema
schema.components.schemas[jobSchemaName].properties.output = { $ref: `#/components/schemas/${outputSchemaName}` }

schema.components.schemas[`Create${jobSchemaName}`] = clone(schema.components.schemas.CreateInferenceEndpointJob)
schema.components.schemas[`Create${jobSchemaName}`].description = `Create a job for ${endpointName}`
schema.components.schemas[`Create${jobSchemaName}`].properties.input = {
    $ref: `#/components/schemas/${inputSchemaName}`,
}

schema.components.schemas[`${jobSchemaName}List`] = clone(schema.components.schemas.InferenceEndpointJobList)
schema.components.schemas[`${jobSchemaName}List`].description = `List of jobs for ${endpointName}`
schema.components.schemas[`${jobSchemaName}List`].properties.items = { $ref: `#/components/schemas/${jobSchemaName}` }

// Request and response bodies
schema.components.requestBodies[`Create${jobSchemaName}`] = clone(
    schema.components.requestBodies.CreateInferenceEndpointJob,
)
schema.components.requestBodies[`Create${jobSchemaName}`].content['application/json'].schema = {
    $ref: `#/components/schemas/Create${jobSchemaName}`,
}

schema.components.responses[`List${jobSchemaName}`] = clone(schema.components.responses.ListInferenceEndpointJobs)
schema.components.responses[`List${jobSchemaName}`].content['application/json'].schema = {
    $ref: `#/components/schemas/${jobSchemaName}List`,
}

schema.components.responses[`Get${jobSchemaName}`] = clone(schema.components.responses.GetInferenceEndpointJob)
schema.components.responses[`Get${jobSchemaName}`].content['application/json'].schema = {
    $ref: `#/components/schemas/${jobSchemaName}`,
}
schema.components.responses[`Create${jobSchemaName}`] = clone(schema.components.responses.CreateInferenceEndpointJob)
schema.components.responses[`Create${jobSchemaName}`].content['application/json'].schema = {
    $ref: `#/components/schemas/${jobSchemaName}`,
}

// Resource: /organizations/{organization_name}/inference-endpoints/{inference_endpoint_name}
const endpointPath = `/organizations/{organization_name}/inference-endpoints/${endpointId}`
schema.paths[endpointPath] = clone(
    schema.paths['/organizations/{organization_name}/inference-endpoints/{inference_endpoint_name}'],
)

// Remove the no-longer-needed variable reference
const inferenceEndpointNameParamIndex = schema.paths[endpointPath].parameters.findIndex(
    (param) => param.$ref === '#/components/parameters/inference_endpoint_name',
)
if (inferenceEndpointNameParamIndex !== -1) {
    schema.paths[endpointPath].parameters.splice(inferenceEndpointNameParamIndex, 1)
}
// Resource: /organizations/{organization_name}/inference-endpoints/{inference_endpoint_name}/jobs
schema.paths[`${endpointPath}/jobs`] = clone(
    schema.paths['/organizations/{organization_name}/inference-endpoints/{inference_endpoint_name}/jobs'],
)
schema.paths[`${endpointPath}/jobs`].summary = `Jobs for ${endpointName}`
schema.paths[`${endpointPath}/jobs`].description = `Operations for ${endpointName} jobs`

// Remove the no-longer-needed variable reference
const jobsInferenceEndpointNameParamIndex = schema.paths[`${endpointPath}/jobs`].parameters.findIndex(
    (param) => param.$ref === '#/components/parameters/inference_endpoint_name',
)
if (jobsInferenceEndpointNameParamIndex !== -1) {
    schema.paths[`${endpointPath}/jobs`].parameters.splice(jobsInferenceEndpointNameParamIndex, 1)
}

schema.paths[`${endpointPath}/jobs`].get.summary = `List jobs for ${endpointName}`
schema.paths[`${endpointPath}/jobs`].get.description = `Retrieves a list of jobs for ${endpointName}`
schema.paths[`${endpointPath}/jobs`].get.responses['200'] = {
    $ref: `#/components/responses/List${jobSchemaName}`,
}
schema.paths[`${endpointPath}/jobs`].post.summary = `Create a job for ${endpointName}`
schema.paths[`${endpointPath}/jobs`].post.description = `Creates a job for ${endpointName}`
schema.paths[`${endpointPath}/jobs`].post.requestBody = {
    $ref: `#/components/requestBodies/Create${jobSchemaName}`,
}
schema.paths[`${endpointPath}/jobs`].post.responses['201'] = {
    $ref: `#/components/responses/Create${jobSchemaName}`,
}

// Resource: /organizations/{organization_name}/inference-endpoints/{inference_endpoint_name}/jobs/{job_id}
schema.paths[`${endpointPath}/jobs/{job_id}`] = clone(
    schema.paths[
        '/organizations/{organization_name}/inference-endpoints/{inference_endpoint_name}/jobs/{inference_endpoint_job_id}'
    ],
)
schema.paths[`${endpointPath}/jobs/{job_id}`].summary = `Job for ${endpointName}`
schema.paths[`${endpointPath}/jobs/{job_id}`].description = `Operations for a ${endpointName} job`

// Remove the no-longer-needed variable reference
const jobInferenceEndpointNameParamIndex = schema.paths[`${endpointPath}/jobs/{job_id}`].parameters.findIndex(
    (param) => param.$ref === '#/components/parameters/inference_endpoint_name',
)
if (jobInferenceEndpointNameParamIndex !== -1) {
    schema.paths[`${endpointPath}/jobs/{job_id}`].parameters.splice(jobInferenceEndpointNameParamIndex, 1)
}

schema.paths[`${endpointPath}/jobs/{job_id}`].get.summary = `Get job for ${endpointName}`
schema.paths[`${endpointPath}/jobs/{job_id}`].get.description = `Retrieves a job for ${endpointName}`
schema.paths[`${endpointPath}/jobs/{job_id}`].get.responses['200'] = {
    $ref: `#/components/responses/Get${jobSchemaName}`,
}

schema.paths[`${endpointPath}/jobs/{job_id}`].delete.summary = `Delete job for ${endpointName}`

fs.writeFileSync(config.baseSchema, JSON.stringify(schema, null, 2))
