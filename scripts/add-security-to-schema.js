const { parse, stringify } = require('yaml')
const fs = require('fs')
const path = require('path')

const usage = `
Usage: node scripts/add-security-to-schema.js <schema-to-modify>

This script adds the security schema from the base schema to the schema to modify, and enables it for every endpoint.
Base schema and schema to modify can be in either JSON or YAML format.
`

/**
 * Load the base schema
 */
const apiSpecDir = 'api-specs'
const baseSchema = 'salad-cloud'
const schema = fs.readdirSync(apiSpecDir).find((file) => path.basename(file, path.extname(file)) === baseSchema)
const schemaPath = path.join(apiSpecDir, schema)
const schemaFile = fs.readFileSync(schemaPath, 'utf8')
const schemaObj = schema.endsWith('.json') ? JSON.parse(schemaFile) : parse(schemaFile)

/**
 * Load the schema to modify
 */
const schemaToModify = process.argv[2]
if (!schemaToModify) {
    console.error(usage)
    process.exit(1)
}
const schemaToModifyFile = fs.readFileSync(schemaToModify, 'utf8')
const outputIsJson = schemaToModify.endsWith('.json')
const schemaToModifyObj = outputIsJson ? JSON.parse(schemaToModifyFile) : parse(schemaToModifyFile)

/**
 * Add the security schema from the base schema to the schema to modify, and enable it for every endpoint
 */
schemaToModifyObj.components.securitySchemes = schemaObj.components.securitySchemes
const nameOfScheme = Object.keys(schemaObj.components.securitySchemes)[0]
schemaToModifyObj.security = [{}, { [nameOfScheme]: [] }]

/**
 * Write the modified schema back to the file
 */
const output = outputIsJson ? JSON.stringify(schemaToModifyObj, null, 2) : stringify(schemaToModifyObj)
fs.writeFileSync(schemaToModify, output)
