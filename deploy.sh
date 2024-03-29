#!/bin/bash -x

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