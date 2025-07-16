#! /bin/bash

python scripts/resolve-redirect-chains.py docs.json
python scripts/update-links.py docs.json
python scripts/remove-redirects-by-prefix "/container-engine/" # This will need to stop happening once this branch goes live
npx prettier --write container-engine
npx prettier --write transcription
npx prettier --write general
npx prettier --write storage
npx prettier --write gateway-service
npx prettier --write docs.json
