#!/usr/bin/env node
/**
 * Script to add required Metadata header to all endpoints in OpenAPI specifications.
 *
 * This script automatically adds the required "Metadata: true" header parameter
 * to all HTTP operations in an OpenAPI YAML specification file.
 *
 * Usage:
 *     node add-metadata-header.js <input-file> [output-file]
 *
 * If output-file is not specified, the input file will be modified in place.
 */

const fs = require('fs')
const path = require('path')
const yaml = require('yaml')

/**
 * Add the Metadata header parameter to a single operation if it doesn't exist.
 * @param {Object} operation - The OpenAPI operation object
 * @returns {boolean} - True if header was added, false if it already existed
 */
function addMetadataHeaderToOperation(operation) {
    const metadataParam = {
        name: 'Metadata',
        in: 'header',
        required: true,
        schema: {
            type: 'string',
            enum: ['true'],
        },
        description: 'Required header to indicate metadata request',
    }

    // Initialize parameters if it doesn't exist
    if (!operation.parameters) {
        operation.parameters = []
    }

    // Check if Metadata header already exists
    for (const param of operation.parameters) {
        if (param.name === 'Metadata' && param.in === 'header') {
            console.log('  Metadata header already exists, skipping...')
            return false
        }
    }

    // Add the metadata header parameter at the beginning
    operation.parameters.unshift(metadataParam)
    return true
}

/**
 * Process the OpenAPI specification and add Metadata headers to all operations.
 * @param {Object} specData - The parsed OpenAPI specification
 * @returns {boolean} - True if any changes were made
 */
function processOpenApiSpec(specData) {
    if (!specData.paths) {
        console.log("No 'paths' section found in OpenAPI spec")
        return false
    }

    let changesMade = false

    for (const [pathName, pathItem] of Object.entries(specData.paths)) {
        console.log(`Processing path: ${pathName}`)

        // Process each HTTP method in this path
        const httpMethods = ['get', 'post', 'put', 'patch', 'delete', 'head', 'options', 'trace']

        for (const method of httpMethods) {
            if (pathItem[method]) {
                const operation = pathItem[method]
                console.log(`  Adding Metadata header to ${method.toUpperCase()} operation...`)

                if (addMetadataHeaderToOperation(operation)) {
                    changesMade = true
                    console.log(`  ✓ Added Metadata header to ${method.toUpperCase()} ${pathName}`)
                }
            }
        }
    }

    return changesMade
}

/**
 * Main function to handle command line arguments and process the file.
 */
function main() {
    const args = process.argv.slice(2)

    if (args.length === 0 || args.includes('--help') || args.includes('-h')) {
        console.log('Usage: node add-metadata-header.js <input-file> [output-file] [--dry-run]')
        console.log('')
        console.log('Options:')
        console.log('  --dry-run    Show what would be changed without modifying files')
        console.log('  --help, -h   Show this help message')
        console.log('')
        console.log('If output-file is not specified, the input file will be modified in place.')
        process.exit(0)
    }

    const dryRun = args.includes('--dry-run')
    const fileArgs = args.filter((arg) => !arg.startsWith('--'))

    if (fileArgs.length === 0) {
        console.error('Error: Input file is required')
        process.exit(1)
    }

    const inputFile = fileArgs[0]
    const outputFile = fileArgs[1] || inputFile

    if (!fs.existsSync(inputFile)) {
        console.error(`Error: Input file '${inputFile}' does not exist`)
        process.exit(1)
    }

    console.log(`Reading OpenAPI spec from: ${inputFile}`)

    try {
        // Load the YAML file
        const fileContent = fs.readFileSync(inputFile, 'utf8')
        const specData = yaml.parse(fileContent)

        console.log('Successfully loaded OpenAPI specification')

        // Process the specification
        const changesMade = processOpenApiSpec(specData)

        if (!changesMade) {
            console.log('No changes needed - all endpoints already have the Metadata header')
            return
        }

        if (dryRun) {
            console.log('\nDry run mode - no files were modified')
            console.log('The following changes would be made:')
            console.log("- Metadata header would be added to operations that don't have it")
            return
        }

        // Write the modified specification
        console.log(`\nWriting updated specification to: ${outputFile}`)

        const updatedYaml = yaml.stringify(specData, {
            lineWidth: 0,
            minContentWidth: 0,
            indent: 2,
        })

        fs.writeFileSync(outputFile, updatedYaml, 'utf8')

        console.log('✓ Successfully updated OpenAPI specification with Metadata headers')
    } catch (error) {
        if (error.name === 'YAMLParseError') {
            console.error(`Error parsing YAML file: ${error.message}`)
        } else {
            console.error(`Error processing file: ${error.message}`)
        }
        process.exit(1)
    }
}

// Run the script if called directly
if (require.main === module) {
    main()
}

module.exports = {
    addMetadataHeaderToOperation,
    processOpenApiSpec,
}
