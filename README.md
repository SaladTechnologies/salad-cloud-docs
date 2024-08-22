# SaladCloud Docs

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

Run the following command at the root of your documentation (where `mint.json` is)

```
mintlify dev
```

### Modifying Site Navigation

All navigation within the mintlify site is managed using `mint.json`. There are three sections of the `mint.json` file that are of concern.

First, the `tabs` array near the top of the file defines the entries in the top sidebar of the live website. To create a new tab, add a new entry to the array. The two elements of the entry are `"name"`, which is the title of that tab as seen in the live website, and `"url"`, which is both the url slug used by the web navigation and the name of the folder in the repo where all files pertaining to that tab are stored. As such, this folder with such a name must also be created.

Second, the `navigation` array, which is the majority of the file. This array defines where each page exists within the website's navigation. When adding a new page to an existing `group`, simply add the directory path of that page to the relevant group. When adding a new page to a new group, the new group object must be created. A group object has two elements: the first, `"group"`, is the name of that group as seen in the website's left-hand sidebar. The second, `"pages"` is an array which can contain either the file paths of `.mdx` files pertaining to webpages within that group, *or* additional group objects for subgroups of pages. (Do not nest group objects further than two deep; i.e. do not place a group object within the pages array of a group object which is *itself* in the pages array of another group object.)

By convention, when creating a nested subgroup, place all relevant `.mdx` files, other than the 'landing' page for the group, within a subdirectory of the parent tab. In other words, when creating a subgroup of an existing group (e.g. `Container Engine` > `Container Groups` > `Container Registries` in the live site), place the 'landing' page within the root directory of the tag (e.g. `container-engine/container-registries`) and all other page files within that subgroup in a relevant subdirectory (e.g. `container-engine/registries`).

Groups will automatically be placed in the relevant tab based on the folders in which the `.mdx` files within that group can be found. In other words, if you create a group entirely from files within the `gateway-service` folder, that group will be reachable from the `Gateway Service` tab in the live site.

Third, the `redirects` array, near the bottom of the file. This controls all redirection where a link may refer to a broken or moved page. Where such is necessary, add a new entry to this array, where the `source` element is the url you want to redirect, and the `destination` element is the location you want the user to be sent instead. (E.g. if I navigate to https://docs.salad.com/docs/sdxl in my browser, I am redirected to https://docs.salad.com/container-engine/gateway/enabling-ipv6.)

### Publishing Changes

Push up your changes to the repo, they will get merged with the live site ASAP.

### Updating the OpenAPI spec

1. Update the spec in the `./api-reference/openapi.json
2. Automatically generate all the files from the spec
   `npx @mintlify/scraping@latest openapi-file ./api-reference/openapi.json -o api-reference`

### Additional Resources

- If you use VSCode, mintlify has an extention for `.mdx` files https://marketplace.visualstudio.com/items?itemName=mintlify.mintlify-snippets
