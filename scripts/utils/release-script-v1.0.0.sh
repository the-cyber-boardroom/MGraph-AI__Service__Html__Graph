#!/bin/bash
# release-v1.0.0.sh
# Script to automate the v1.0.0 release process

set -e  # Exit on error

echo "🚀 Starting v1.0.0 release process..."

# Ensure we're on dev branch
echo "📍 Checking out dev branch..."
git checkout dev
git pull origin dev

# Update version in files
echo "📝 Updating version to v1.0.0..."
echo "v1.0.0" > mgraph_ai_service_html__graph/version

# Update README.md - handle both macOS and Linux sed
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    sed -i '' 's/release-v[0-9]\+\.[0-9]\+\.[0-9]\+/release-v1.0.0/g' README.md
    sed -i '' 's/version     = "v[0-9]\+\.[0-9]\+\.[0-9]\+"/version     = "v1.0.0"/g' pyproject.toml
else
    # Linux
    sed -i 's/release-v[0-9]\+\.[0-9]\+\.[0-9]\+/release-v1.0.0/g' README.md
    sed -i 's/version     = "v[0-9]\+\.[0-9]\+\.[0-9]\+"/version     = "v1.0.0"/g' pyproject.toml
fi

# Show what changed
echo "📋 Changes to be committed:"
git diff mgraph_ai_service_html__graph/version README.md pyproject.toml

# Commit changes
echo "💾 Committing changes..."
git add mgraph_ai_service_html__graph/version README.md pyproject.toml
git commit -m "Release v1.0.0"

# Tag the commit
echo "🏷️  Creating tag v1.0.0..."
git tag v1.0.0

# Push changes and tags
echo "⬆️  Pushing to GitHub..."
git push origin dev
git push origin v1.0.0

echo "✅ v1.0.0 released successfully!"
echo ""
echo "📝 Next steps - Create a GitHub Release manually:"
echo "   1. Go to https://github.com/the-cyber-boardroom/MGraph-AI__Service__Html__Graph/releases"
echo "   2. Click 'Create a new release'"
echo "   3. Choose tag: v1.0.0"
echo "   4. Release title: v1.0.0"
echo "   5. Add release notes describing:"
echo "      - Initial production release"
echo "      - FastAPI scaffold with health and info endpoints"
echo "      - Full CI/CD pipeline for dev, qa, and prod"
echo "      - AWS Lambda deployment ready"
echo "      - Type-safe architecture"
echo "   6. Click 'Publish release'"
echo ""
echo "🎉 After creating the GitHub release, check that:"
echo "   - CI/CD pipeline runs and creates v1.0.1"
echo "   - New tag v1.0.1 is created automatically"
echo "   - Dev environment updates to v1.0.1"