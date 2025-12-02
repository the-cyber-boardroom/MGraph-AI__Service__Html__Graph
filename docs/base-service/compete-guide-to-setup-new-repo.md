# Complete Guide: Creating MGraph-AI Service from Template

This guide documents the exact steps to create a new MGraph-AI service from the base template, as successfully executed for `MGraph-AI__Service__Graphs`.

## Prerequisites

- GitHub account with access to create repositories in `the-cyber-boardroom` organization
- Git installed locally
- Python 3.12+ installed
- PyCharm or similar IDE (optional but recommended)
- AWS account with appropriate permissions
- AWS CLI configured locally

## Step 1: Create Empty Repository on GitHub

1. Go to GitHub and create a new repository
2. Name it following the pattern: `MGraph-AI__Service__YourName`
   - Example: `MGraph-AI__Service__Graphs`
3. **IMPORTANT**: Create as a completely empty repository:
   - ❌ Do NOT add README
   - ❌ Do NOT add .gitignore
   - ❌ Do NOT add license
   - Leave "Add a README file" unchecked
   - Set to "Public" visibility

## Step 2: Clone and Setup Template

```bash
# Clone your empty repository
git clone git@github.com:the-cyber-boardroom/MGraph-AI__Service__Graphs.git
cd MGraph-AI__Service__Graphs

# Create and checkout dev branch first
git checkout -b dev

# Add the template repository as a remote
git remote add template https://github.com/the-cyber-boardroom/MGraph-AI__Service__Html__Graph.git

# Fetch and merge template
git fetch template
git merge template/main --allow-unrelated-histories -m "Initial import from MGraph-AI__Service__Html__Graph template"
```

## Step 3: Rename Service

### Option A: Using the rename script (if available)
```bash
./scripts/rename-service.sh mgraph_ai_service_graphs
```

### Option B: Manual rename
```bash
# Rename the main directory
mv mgraph_ai_service_html__graph mgraph_ai_service_graphs
```

## Step 4: Global Search and Replace

Open the project in PyCharm (or your preferred IDE) and perform these global search and replace operations:

1. **Replace "MGraph AI Service Html Graph"** → **"MGraph-AI Service Graphs"**
   - Should find ~10 occurrences
   - These are in documentation and comments

2. **Replace "mgraph_ai_service_html__graph"** → **"mgraph_ai_service_graphs"**
   - Should find 1-2 occurrences (after rename script)
   - This is the Python package name

3. **Replace "MGraph-AI__Service__Html__Graph"** → **"MGraph-AI__Service__Graphs"**
   - Should find ~35 occurrences
   - These are in README, documentation, and GitHub URLs

**PyCharm Instructions:**
- Use `Cmd+Shift+R` (Mac) or `Ctrl+Shift+R` (Windows/Linux) for Replace in Files
- Check "Match case" for accuracy
- Review each replacement before applying

## Step 5: Update Service Configuration

Edit `mgraph_ai_service_graphs/config.py`:

```python
from mgraph_ai_service_graphs import package_name

SERVICE_NAME                             = package_name
FAST_API__TITLE                          = "MGraph-AI Service Graphs"  # Update this line
FAST_API__DESCRIPTION                    = "Graph management and operations service"
LAMBDA_DEPENDENCIES__FAST_API_SERVERLESS = ['osbot-fast-api-serverless==v1.2.0']
```

## Step 6: Update Version

```bash
echo "v0.1.0" > mgraph_ai_service_graphs/version
```

## Step 7: Create Template Tracking (Optional)

```bash
mkdir -p .template
cat > .template/VERSION << EOF
TEMPLATE_VERSION=0.3.0
CREATED_DATE=$(date -u +%Y-%m-%d)
SERVICE_NAME=mgraph_ai_service_graphs
REPO_NAME=MGraph-AI__Service__Graphs
EOF
```

## Step 8: Install Dependencies

```bash
# Install test requirements
pip install -r requirements-test.txt

# Install package in development mode
pip install -e .
```

## Step 9: Configure PyCharm for Testing

1. Open PyCharm Settings/Preferences
2. Go to Tools → Python Integrated Tools
3. Set "Default test runner" to "pytest"
4. Apply and close

## Step 10: Run Tests Locally

In PyCharm:
- Right-click on `tests` folder → Run 'pytest in tests'
- All tests should pass (17 tests, some may be skipped if no AWS credentials)

Or from command line:
```bash
pytest tests/unit/
```

## Step 11: Commit and Push Changes

```bash
# Add all changes
git add .

# Commit with descriptive message
git commit -m "Initialize MGraph-AI Service Graphs from template

- Based on MGraph-AI__Service__Html__Graph v0.3.0
- Service name: mgraph_ai_service_graphs
- Repository: MGraph-AI__Service__Graphs
- All tests passing"

# Push to GitHub dev branch
git push -u origin dev
```

## Step 12: Configure GitHub Secrets

1. Go to your repository on GitHub
2. Navigate to Settings → Secrets and variables → Actions
3. Add the following repository secrets:

| Secret Name | Description | Example Value |
|------------|-------------|---------------|
| `AWS_ACCESS_KEY_ID` | AWS access key | `AKIAIOSFODNN7EXAMPLE` |
| `AWS_SECRET_ACCESS_KEY` | AWS secret key | `wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY` |
| `AWS_DEFAULT_REGION` | AWS region | `eu-west-2` or `us-east-1` |
| `AWS_ACCOUNT_ID` | AWS account ID | `123456789012` |
| `FAST_API__AUTH__API_KEY__NAME` | Header name for API key | `x-api-key` |
| `FAST_API__AUTH__API_KEY__VALUE` | Actual API key value | Generate a secure random string |

## Step 13: Verify GitHub Actions Deployment

After adding secrets and pushing to dev:

1. Go to Actions tab in GitHub
2. You should see "CI Pipeline - DEV" workflow running
3. Wait for it to complete (takes about 1-2 minutes)
4. All steps should show green checkmarks:
   - ✅ Run tests
   - ✅ Increment Tag
   - ✅ Check AWS Credentials
   - ✅ Deploy to AWS Lambda

## Step 14: Verify AWS Lambda Deployment

1. Log into AWS Console
2. Navigate to Lambda → Functions
3. Find `mgraph_ai_service_graphs_dev` function
4. Note the Function URL (will be something like `https://xxxxx.lambda-url.region.on.aws/`)

## Step 15: Test Deployed Service

```bash
# Set your API key from GitHub secrets
API_KEY="your-api-key-value"
FUNCTION_URL="https://xxxxx.lambda-url.region.on.aws"

# Test health endpoint
curl -H "x-api-key: $API_KEY" $FUNCTION_URL/info/status

# Should return:
# {
#   "name": "mgraph_ai_service_graphs",
#   "version": "v0.1.0",
#   "status": "operational",
#   "environment": "aws-lambda"
# }
```

## Step 16: Create Main Branch (Optional)

```bash
# Create main branch from dev
git checkout -b main
git push -u origin main

# Switch back to dev for development
git checkout dev
```

## Local Development

For local development and testing:

```bash
# Set environment variables
export FAST_API__AUTH__API_KEY__NAME="x-api-key"
export FAST_API__AUTH__API_KEY__VALUE="test-key-123"

# Run the service locally
./scripts/run-locally.sh

# In another terminal, test it
curl -H "x-api-key: test-key-123" http://localhost:10011/info/status
```

## Troubleshooting

### Tests Failing
- Ensure all dependencies are installed: `pip install -r requirements-test.txt`
- Check that pytest is configured in PyCharm
- Some tests require AWS credentials and will skip if not configured

### GitHub Actions Failing
- Check that all GitHub secrets are properly configured
- Verify AWS credentials have necessary permissions for Lambda
- Check the Actions logs for specific error messages

### Lambda Not Deploying
- Ensure AWS credentials in GitHub secrets are valid
- Check AWS account has Lambda service available in the selected region
- Verify the Lambda function name doesn't conflict with existing functions

### Service Not Responding
- Check API key is included in request headers
- Verify the Lambda function URL is correct
- Check CloudWatch logs in AWS for error messages

## Success Checklist

✅ Empty GitHub repository created  
✅ Template merged successfully  
✅ All references renamed from "base" to your service name  
✅ Tests passing locally  
✅ Code committed and pushed to GitHub  
✅ GitHub secrets configured  
✅ GitHub Actions workflow successful  
✅ AWS Lambda function deployed  
✅ Service responding to API calls  

## Next Steps

Now that your service is deployed, you can:

1. **Add service-specific functionality** in `mgraph_ai_service_graphs/service/`
2. **Create new API endpoints** in `mgraph_ai_service_graphs/fast_api/routes/`
3. **Define data schemas** for type safety
4. **Write comprehensive tests** for new features
5. **Set up monitoring** with CloudWatch
6. **Configure custom domain** with API Gateway or CloudFront
7. **Document your API** in the README

## Maintaining Template Connection

To pull future updates from the template:

```bash
# Fetch latest template changes
git fetch template

# Review what changed
git log template/main --oneline

# Merge updates (be prepared to resolve conflicts)
git merge template/main

# Or cherry-pick specific improvements
git cherry-pick <commit-hash>
```

---

**Congratulations!** You've successfully created and deployed a new MGraph-AI service from the template. The service is now live on AWS Lambda with automatic CI/CD deployment on every push to the dev branch.