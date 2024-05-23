# SaladCloud DOcs

### Installation

Install NVM

Windows - https://github.com/coreybutler/nvm-windows
Mac/Linux = https://github.com/nvm-sh/nvm?tab=readme-ov-file#installing-and-updating

Install Node
`nvm install node`

Install the [Mintlify CLI](https://www.npmjs.com/package/mintlify) to preview the documentation changes locally. To install, use the following command

```
npm i -g mintlify
```

Run the following command at the root of your documentation (where mint.json is)

```
mintlify dev
```

### Publishing Changes

Push up your changes to the repo, they will get merged with the live site ASAP.

### Updating the OpenAPI spec

1. Update the spec in the `./api-reference/openapi.json
2. Automatically generate all the files from the spec
   `npx @mintlify/scraping@latest openapi-file ./api-reference/openapi.json -o api-reference`

### Additional Resources

- If you use VSCode, mintlify has an extention for `.mdx` files https://marketplace.visualstudio.com/items?itemName=mintlify.mintlify-snippets
