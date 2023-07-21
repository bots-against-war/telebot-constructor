#! /bin/bash

set -e

# smth like this...
# echo "Building static frontend files from sources"
# cd frontend && npm run build && cd ..

echo "Cleaning possible artifacts from previous build"
mkdir -p telebot_constructor/static
rm telebot_constructor/static/*

echo "Copying frontend into package"
cp frontend/public/* telebot_constructor/static*
