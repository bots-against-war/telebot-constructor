#! /bin/bash

# This is a python package building script, including pre-building frontend and adding it
# as static files inside the package

# TODO: rewrite in python this fucking sucks...

set -e

BASE_PATH="\/constructor-test123"

# smth like this...
# echo "Building static frontend files from sources"
# cd frontend && npm run build && cd ..

echo "Cleaning possible artifacts from previous builds"
rm -rf telebot_constructor/static/
mkdir -p telebot_constructor/static

# this will be done by Vite, so just temporary emulation
echo "Replacing base path in frontend code"
for filename in frontend/public/*; do
    relative_filename="$filename"#frontent/public/
    target_filename=/telebot_constructor/static/$relative_filename
    echo "$relative_filename: copying with sed $filename -> $target_filename"
    sed "s/import\.meta\.env\.BASE_URL/\"${BASE_PATH}\"/" $filename > $target_filename
done

echo "Copying frontend into package"
cp frontend/public/* telebot_constructor/static/

echo "Running poetry build"
# poetry build
