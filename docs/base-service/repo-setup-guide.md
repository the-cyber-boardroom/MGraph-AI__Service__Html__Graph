# MGraph AI Service Html Graph - Setup Guide

This guide walks through the complete setup process from initial repository creation to v1.0.0 release.

## 📋 Prerequisites

- GitHub repository created: `https://github.com/the-cyber-boardroom/MGraph-AI__Service__Html__Graph`
- AWS account with appropriate permissions
- GitHub CLI (`gh`) installed (optional but helpful)
- AWS CLI configured locally

## 🔐 Step 1: Configure GitHub Secrets

In your GitHub repository, go to Settings → Secrets and variables → Actions, and add:

| Secret Name | Description | Example                    |
|-------------|-------------|----------------------------|
| `AWS_SECRET_ACCESS_KEY` | AWS secret key | `wJalrXUtnFEMI/K7MDENG...` |
| `AWS_DEFAULT_REGION` | AWS region | `us-east-1`                |
| `AWS_ACCOUNT_ID` | AWS account ID | `123456789012`             |
| `AWS_ACCESS_KEY_ID` | AWS access key | `AKIAIOSF...`              |
| `FAST_API__AUTH__API_KEY__NAME` | API key header name | `x-api-key`                |
| `FAST_API__AUTH__API_KEY__VALUE` | API key value | `your-secure-api-key-here` |

## 🚀 Step 2: Initial Repository Setup

```bash
# 1. Clone the repository
git clone https://github.com/the-cyber-boardroom/MGraph-AI__Service__Html__Graph.git
cd MGraph-AI__Service__Html__Graph

# 2. Create initial commit (empty repo)
git init
echo "# MGraph AI Service Html Graph" > temp.md
git add temp.md
git commit -m "Initial repository creation"
git branch -M main
git remote add origin https://github.com/the-cyber-boardroom/MGraph-AI__Service__Html__Graph.git
git push -u origin main

# 3. Tag the initial commit with v0.1.0
git tag v0.1.0
git push origin v0.1.0

# 4. Create and switch to dev branch
git checkout -b dev

# 5. Remove temp file
rm temp.md

# 6. Add all the scaffold files (copy all files created above)
# ... copy all files into the repository ...

# 7. Commit the scaffold
git add .
git commit -m "First commit for MGraph AI Service Html Graph - v1.0.0 scaffold with FastAPI setup, tests, and CI/CD pipeline"

# 8. Push to dev branch
git push -u origin dev
```

## ✅ Step 3: Verify Initial Deployment

After pushing to dev:

1. **Check for new tag** (should be v0.1.1):
   ```bash
   git fetch --tags
   git tag -l
   ```

2. **Monitor GitHub Actions**:
   - Go to Actions tab in GitHub
   - Watch the "CI Pipeline - DEV" workflow
   - Ensure all steps complete successfully

3. **Verify AWS Lambda**:
   - Log into AWS Console
   - Navigate to Lambda → Functions
   - Look for `mgraph_ai_service_html_graph-dev`
   - Check Function URL is created

## 🌐 Step 4: Configure CloudFront and DNS

### Naming Convention
- Dev: `dev.base.mgraph.ai`
- QA: `qa.base.mgraph.ai`
- Prod: `prod.base.mgraph.ai`

Pattern: `{stage}.{service-name}.mgraph.ai`

### CloudFront Setup

1. **Create CloudFront Distribution**:
   - Origin Domain: Lambda Function URL (without https://)
   - Origin Protocol Policy: HTTPS Only
   - Viewer Protocol Policy: Redirect HTTP to HTTPS
   - Alternate Domain Names (CNAMEs): `dev.base.mgraph.ai`
   - SSL Certificate: Use ACM certificate for `*.mgraph.ai`

2. **Configure Behaviors**:
   - Path Pattern: Default (*)
   - Allowed HTTP Methods: GET, HEAD, OPTIONS, PUT, POST, PATCH, DELETE
   - Cache Policy: Managed-CachingDisabled
   - Origin Request Policy: Managed-AllViewer

3. **Note the CloudFront Domain Name** (e.g., `d1234567890.cloudfront.net`)

### DNS Configuration

1. **Create Route 53 A Record**:
   - Record name: `dev.base`
   - Record type: A
   - Alias: Yes
   - Route traffic to: CloudFront distribution
   - Select your distribution from the dropdown

2. **Wait for propagation** (usually 1-2 minutes)

3. **Test the domain**:
   ```bash
   curl https://dev.base.mgraph.ai/health
   # Should return: {"status":"healthy","service":"mgraph_ai_service_html_graph"}
   ```

## 📈 Step 5: Release to Main/QA

```bash
# 1. Ensure you're on dev branch with all changes pushed
git checkout dev
git pull origin dev

# 2. Run the release script
./scripts/gh-release-to-main.sh

# This script will:
# - Checkout main
# - Merge dev into main (no-ff)
# - Push to main
# - Checkout dev again
# - Merge main back into dev
```

3. **Verify QA deployment**:
   - Check GitHub Actions for "CI Pipeline - MAIN" workflow
   - Version should increment to v0.2.0
   - Lambda function `mgraph_ai_service_html_graph-qa` should be created
   - Repeat CloudFront/DNS setup for `qa.base.mgraph.ai`

## 🚢 Step 6: Deploy to Production

1. **Manually trigger production deployment**:
   - Go to GitHub Actions
   - Select "CI Pipeline - Prod" workflow
   - Click "Run workflow"
   - Select `main` branch
   - Click "Run workflow"

2. **Verify production deployment**:
   - Lambda function `mgraph_ai_service_html_graph-prod` should be created
   - Repeat CloudFront/DNS setup for `prod.base.mgraph.ai`

## 🏷️ Step 7: Release v1.0.0

Create a helper script `release-v1.0.0.sh`:

```bash
#!/bin/bash
# release-v1.0.0.sh

# Ensure we're on dev branch
git checkout dev
git pull origin dev

# Update version in files
echo "v1.0.0" > mgraph_ai_service_html_graph/version

# Update README.md
sed -i '' 's/release-v[0-9]\+\.[0-9]\+\.[0-9]\+/release-v1.0.0/g' README.md

# Update pyproject.toml
sed -i '' 's/version     = "v[0-9]\+\.[0-9]\+\.[0-9]\+"/version     = "v1.0.0"/g' pyproject.toml

# Commit changes
git add mgraph_ai_service_html_graph/version README.md pyproject.toml
git commit -m "Release v1.0.0"

# Tag the commit
git tag v1.0.0

# Push changes and tags
git push origin dev
git push origin v1.0.0

echo "✅ v1.0.0 released!"
echo "📝 Now create a GitHub Release manually:"
echo "   1. Go to https://github.com/the-cyber-boardroom/MGraph-AI__Service__Html__Graph/releases"
echo "   2. Click 'Create a new release'"
echo "   3. Choose tag: v1.0.0"
echo "   4. Release title: v1.0.0"
echo "   5. Describe the release"
echo "   6. Click 'Publish release'"
```

Make it executable:
```bash
chmod +x release-v1.0.0.sh
```

Run it:
```bash
./release-v1.0.0.sh
```

## ✅ Step 8: Final Verification

After completing all steps:

1. **Check versions**:
   ```bash
   git fetch --tags
   git tag -l
   # Should show: v0.1.0, v0.1.1, v0.2.0, v0.2.1, v1.0.0, v1.0.1
   ```

2. **Verify all environments**:
   ```bash
   # Dev environment
   curl https://dev.base.mgraph.ai/info/version
   # Should return: {"version":"v1.0.1"}

   # QA environment
   curl https://qa.base.mgraph.ai/info/version
   # Should return: {"version":"v0.2.0"}

   # Prod environment
   curl https://prod.base.mgraph.ai/info/version
   # Should return: {"version":"v0.2.0"}
   ```

3. **Check GitHub Release**:
   - Navigate to Releases page
   - Verify v1.0.0 release is published

## 🎯 Summary

You now have:
- ✅ Three environments (dev, qa, prod) fully deployed
- ✅ CloudFront distributions for each environment
- ✅ DNS configured for clean URLs
- ✅ Automated CI/CD pipeline
- ✅ Version v1.0.0 released and tagged
- ✅ All environments accessible via HTTPS

## 🔧 Troubleshooting

### Lambda Function URL Not Working
- Check Lambda function exists
- Verify Function URL is enabled
- Check IAM permissions

### CloudFront 403/404 Errors
- Verify Origin Domain is correct
- Check Origin Protocol Policy is HTTPS Only
- Ensure Lambda Function URL is accessible

### DNS Not Resolving
- Wait 2-5 minutes for propagation
- Check Route 53 record points to correct CloudFront distribution
- Verify CloudFront alternate domain names include your domain

### GitHub Actions Failing
- Check AWS credentials are set correctly
- Verify IAM permissions for Lambda deployment
- Check GitHub Actions logs for specific errors

## 📝 Notes

- The service naming convention is important for consistency: `{stage}.{service-name}.mgraph.ai`
- Always test in dev before promoting to qa/prod
- Keep the release notes updated for each version
- Monitor AWS costs, especially for Lambda invocations and CloudFront requests

---

This completes the setup! Your MGraph AI Service Html Graph is now fully operational across all environments.