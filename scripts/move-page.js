const fs = require('fs')
const path = require('path')

const usage = `
Usage: move-page.js <source> <destination>

Moves a page from one location to another, updating all links, and adding a redirect to mint.json
`

let src = process.argv[2]
let dest = process.argv[3]

if (!src || !dest) {
    console.error(usage)
    process.exit(1)
}

if (!src.endsWith('.mdx')) {
    src += '.mdx'
}

if (!dest.endsWith('.mdx')) {
    dest += '.mdx'
}

if (!fs.existsSync(src)) {
    console.error(`Source file does not exist: ${src}`)
    process.exit(1)
}

if (fs.existsSync(dest)) {
    console.error(`Destination file already exists: ${dest}`)
    process.exit(1)
}

fs.mkdirSync(path.dirname(dest), { recursive: true })

/**
 * name is the relative path from the root of the project to the source file, without the leading slash,
 * and with the file extension removed.
 *  */
const srcName = path.relative(process.cwd(), src).slice(0, -path.extname(src).length)
const srcPath = `/${srcName}`
const destName = path.relative(process.cwd(), dest).slice(0, -path.extname(dest).length)
const destPath = `/${destName}`

const mint = require('../mint.json')

// Move the page
fs.renameSync(src, dest)

// Add the redirect
mint.redirects.push({
    source: srcPath,
    destination: destPath,
})

/*
 * Update the navigation array in mint.json, which is a recursive structure of { group, pages }, where pages is an array
 * of either strings or objects with group and pages.
 * */
function updateNavigation(navigation, updated = []) {
    for (let item of navigation) {
        if (typeof item === 'string') {
            if (item === srcPath) {
                updated.push(destPath)
            } else {
                updated.push(item)
            }
        } else {
            const group = { ...item }
            group.pages = updateNavigation(group.pages)
            updated.push(group)
        }
    }

    return updated
}
mint.navigation = updateNavigation(mint.navigation)

fs.writeFileSync('mint.json', JSON.stringify(mint, null, 2))
