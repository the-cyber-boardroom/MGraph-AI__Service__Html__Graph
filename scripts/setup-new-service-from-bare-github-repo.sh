#!/bin/bash
# scripts/setup-mgraph-service.sh
# Complete setup script for creating a new MGraph-AI service from template
set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_step() { echo -e "${BLUE}==>${NC} $1"; }
print_success() { echo -e "${GREEN}✅${NC} $1"; }
print_warning() { echo -e "${YELLOW}⚠️${NC} $1"; }
print_error() { echo -e "${RED}❌${NC} $1"; }

# Check if repository name is provided
if [ -z "$1" ]; then
    echo "Usage: ./setup-mgraph-service.sh <Repository-Name>"
    echo "Example: ./setup-mgraph-service.sh MGraph-AI__Service__Personas"
    echo ""
    echo "Prerequisites:"
    echo "1. Create an empty repository on GitHub with the name you provide"
    echo "2. Do NOT add README, .gitignore, or license when creating the repo"
    exit 1
fi

REPO_NAME="$1"
SERVICE_NAME_UNDERSCORES=$(echo "$REPO_NAME" | sed 's/MGraph-AI__Service__/mgraph_ai_service_/' | tr '[:upper:]' '[:lower:]')
SERVICE_NAME_TITLE=$(echo "$REPO_NAME" | sed 's/__/ /g' | sed 's/-/ /g')

print_step "Setting up new MGraph-AI service: $REPO_NAME"
print_step "Python package name will be: $SERVICE_NAME_UNDERSCORES"
print_step "Service title will be: $SERVICE_NAME_TITLE"
echo ""

# Step 1: Clone the empty repository
print_step "Cloning repository $REPO_NAME..."
if [ -d "$REPO_NAME" ]; then
    print_warning "Directory $REPO_NAME already exists. Removing it..."
    rm -rf "$REPO_NAME"
fi

git clone "git@github.com:the-cyber-boardroom/$REPO_NAME.git"
cd "$REPO_NAME"
print_success "Repository cloned"

# Step 2: Create and checkout dev branch
print_step "Creating dev branch..."
git checkout -b dev
print_success "Dev branch created"

# Step 3: Add template repository as remote
print_step "Adding template repository..."
git remote add template https://github.com/the-cyber-boardroom/MGraph-AI__Service__Html__Graph.git
print_success "Template remote added"

# Step 4: Fetch and merge template
print_step "Fetching and merging template..."
git fetch template
git merge template/main --allow-unrelated-histories -m "Initial import from MGraph-AI__Service__Html__Graph template"
print_success "Template merged"

# Step 5: Rename the service directory
print_step "Renaming service directory from mgraph_ai_service_html_graph to $SERVICE_NAME_UNDERSCORES..."
if [ -d "mgraph_ai_service_html_graph" ]; then
    mv mgraph_ai_service_html_graph "$SERVICE_NAME_UNDERSCORES"
    print_success "Service directory renamed"
else
    print_error "mgraph_ai_service_html_graph directory not found!"
    exit 1
fi

# Step 6: Global search and replace operations
print_step "Performing global replacements..."

# Function to perform replacement in all relevant files
replace_in_files() {
    local search="$1"
    local replace="$2"
    local description="$3"

    # Count occurrences before replacement
    count=$(grep -r "$search" . --include="*.py" --include="*.md" --include="*.yml" --include="*.yaml" --include="*.toml" --include="*.sh" --include="*.txt" --include="*.json" --exclude-dir=.git --exclude-dir=__pycache__ 2>/dev/null | wc -l | tr -d ' ')

    if [ "$count" -gt 0 ]; then
        print_step "  Replacing '$search' with '$replace' ($count occurrences)..."

        # Perform replacement
        find . -type f \( -name "*.py" -o -name "*.md" -o -name "*.yml" -o -name "*.yaml" -o -name "*.toml" -o -name "*.sh" -o -name "*.txt" -o -name "*.json" \) -not -path "./.git/*" -not -path "*/__pycache__/*" -exec sed -i.bak "s|$search|$replace|g" {} \;

        # Clean up backup files
        find . -name "*.bak" -type f -delete

        print_success "  Replaced $count occurrences of $description"
    else
        print_warning "  No occurrences found for '$search'"
    fi
}

# Replace "MGraph AI Service Html Graph" with the new service title
replace_in_files "MGraph AI Service Html Graph" "$SERVICE_NAME_TITLE" "service title"

# Replace "mgraph_ai_service_html_graph" with the new package name
replace_in_files "mgraph_ai_service_html_graph" "$SERVICE_NAME_UNDERSCORES" "Python package name"

# Replace "MGraph-AI__Service__Html__Graph" with the new repository name
replace_in_files "MGraph-AI__Service__Html__Graph" "$REPO_NAME" "repository name"

print_success "All replacements completed"

# Step 7: Update service configuration
print_step "Updating service configuration..."
CONFIG_FILE="$SERVICE_NAME_UNDERSCORES/config.py"
if [ -f "$CONFIG_FILE" ]; then
    # Update the FAST_API__TITLE if it wasn't already updated
    sed -i.bak "s/FAST_API__TITLE.*=.*/FAST_API__TITLE                          = \"$SERVICE_NAME_TITLE\"/" "$CONFIG_FILE"
    rm -f "$CONFIG_FILE.bak"
    print_success "Configuration updated"
else
    print_warning "Config file not found at $CONFIG_FILE"
fi

# Step 8: Update version file
print_step "Setting initial version..."
echo "v0.1.0" > "$SERVICE_NAME_UNDERSCORES/version"
print_success "Version set to v0.1.0"

# Step 9: Create template tracking file
print_step "Creating template tracking file..."
mkdir -p .template
cat > .template/VERSION << EOF
TEMPLATE_VERSION=0.3.0
CREATED_DATE=$(date -u +%Y-%m-%d)
SERVICE_NAME=$SERVICE_NAME_UNDERSCORES
REPO_NAME=$REPO_NAME
EOF
print_success "Template tracking file created"

# Step 10: Commit and push changes
print_step "Committing changes..."
git add .
git commit -m "Initialize $SERVICE_NAME_TITLE from template

- Based on MGraph-AI__Service__Html__Graph v0.3.0
- Service name: $SERVICE_NAME_UNDERSCORES
- Repository: $REPO_NAME
- Automated setup complete"
print_success "Changes committed"

print_step "Pushing to GitHub dev branch..."
git push -u origin dev
print_success "Pushed to GitHub"

# Final success message
echo ""
echo "========================================="
echo ""
print_success "Setup complete! 🎉"
echo ""
echo "Repository: $REPO_NAME"
echo "Package: $SERVICE_NAME_UNDERSCORES"
echo "Title: $SERVICE_NAME_TITLE"
echo ""
echo "========================================="