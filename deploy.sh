#!/bin/bash -x

# NOTE - CodeBuild and CodePipeline both have hooks to deploy this code on commit. As of 10/25/24 it wasn't building properly, and needed a manual build from this machine. Need to find out which of them (if either) can build it correctly
# Update 1/25/25: The local shared module reference has an absolute path which is breaking things.
# poetry export doesn't work: "The command "export" does not exist."

poetry export -C menu_suggester -f requirements.txt --output menu_suggester/src/menu_suggester/requirements.txt --without-hashes
poetry export -C paprika_fetcher -f requirements.txt --output paprika_fetcher/src/paprika_fetcher/requirements.txt --without-hashes
poetry export -C shared -f requirements.txt --output shared/src/dinner_optimizer_shared/requirements.txt --without-hashes
poetry export -C upcoming_reminder -f requirements.txt --output upcoming_reminder/src/upcoming_reminder/requirements.txt --without-hashes
poetry export -C user_response_recorder -f requirements.txt --output user_response_recorder/src/user_response_recorder/requirements.txt --without-hashes

sam build --no-cached

if [ -z "$CI" ]; then
    sam deploy --guided
else
    sam deploy --capabilities CAPABILITY_IAM --no-fail-on-empty-changeset --no-confirm-changeset --no-progressbar
fi