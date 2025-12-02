#!/bin/bash
# Update version across all files

if [ -z "$1" ]; then
    echo "Usage: ./scripts/update-version.sh <version>"
    echo "Example: ./scripts/update-version.sh v1.0.0"
    exit 1
fi

NEW_VERSION=$1

# Update version file
echo -n "$NEW_VERSION" > mgraph_ai_service_html_graph/version

# Update pyproject.toml
if [[ "$OSTYPE" == "darwin"* ]]; then
    sed -i '' "s/version     = \"v[0-9]\+\.[0-9]\+\.[0-9]\+\"/version     = \"$NEW_VERSION\"/g" pyproject.toml
else
    sed -i "s/version     = \"v[0-9]\+\.[0-9]\+\.[0-9]\+\"/version     = \"$NEW_VERSION\"/g" pyproject.toml
fi

# Update README.md badge
if [[ "$OSTYPE" == "darwin"* ]]; then
    sed -i '' "s/release-v[0-9]\+\.[0-9]\+\.[0-9]\+/release-$NEW_VERSION/g" README.md
else
    sed -i "s/release-v[0-9]\+\.[0-9]\+\.[0-9]\+/release-$NEW_VERSION/g" README.md
fi

echo "✅ Version updated to $NEW_VERSION"