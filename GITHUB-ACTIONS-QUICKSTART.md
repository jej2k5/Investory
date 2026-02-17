# GitHub Actions Quick Reference

## 🚀 Quick Start

### First Time Setup

1. **Fork the repository** on GitHub

2. **Enable GitHub Actions**
   - Already enabled by default
   - Go to Actions tab to verify

3. **Configure Container Registry**
   - Go to Settings → Packages
   - Images will automatically push to `ghcr.io/YOUR_USERNAME/investory`

4. **No secrets required!** 
   - GitHub Actions works out of the box
   - Optional secrets for integrations (SonarCloud, Codecov, Slack)

### Using the Workflows

**Every Push to Main/Develop:**
- ✅ Code is linted
- ✅ Tests run automatically
- ✅ Docker images built
- ✅ Images pushed to GitHub Container Registry

**Every Pull Request:**
- ✅ All CI checks run
- ✅ Docker images built (not pushed)
- ✅ Integration tests run
- ✅ Must pass before merge

**Every Version Tag (v*):**
- ✅ GitHub release created
- ✅ Changelog generated
- ✅ Production images built
- ✅ Images tagged with version

## 📦 Accessing Your Docker Images

After pushing to GitHub, your images are available at:

```bash
# Latest images
docker pull ghcr.io/YOUR_USERNAME/investory/backend:latest
docker pull ghcr.io/YOUR_USERNAME/investory/frontend:latest

# Specific version
docker pull ghcr.io/YOUR_USERNAME/investory/backend:v1.0.0

# Use in docker compose.yml
services:
  backend:
    image: ghcr.io/YOUR_USERNAME/investory/backend:latest
```

### Make Images Public

1. Go to Packages (right sidebar on GitHub)
2. Click on your package (backend or frontend)
3. Package settings → Change visibility → Public

## 🏷️ Creating Releases

### Method 1: Using Git Tags

```bash
# Create and push a tag
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0

# This triggers:
# 1. Release workflow
# 2. Changelog generation
# 3. GitHub release creation
# 4. Docker image builds with version tags
```

### Method 2: Using GitHub CLI

```bash
# Install GitHub CLI
brew install gh  # macOS
# or visit: https://cli.github.com/

# Create release
gh release create v1.0.0 --generate-notes --title "Version 1.0.0"
```

### Method 3: Using GitHub Web UI

1. Go to Releases → Draft a new release
2. Click "Choose a tag" → Create new tag: v1.0.0
3. Click "Generate release notes"
4. Publish release

## 🔄 Workflow Triggers

| Workflow | Trigger | What It Does |
|----------|---------|--------------|
| `ci.yml` | Push to main/develop, PRs | Runs tests and linting |
| `docker-build.yml` | Push to main/develop, PRs, tags | Builds Docker images |
| `release.yml` | Version tags (v*) | Creates releases |

## 📊 Viewing Workflow Results

### In GitHub UI
1. Go to **Actions** tab
2. Click on a workflow run
3. View logs and results

### Using GitHub CLI
```bash
# List recent runs
gh run list

# View specific run
gh run view RUN_ID

# Download logs
gh run download RUN_ID
```

## 🐛 Common Issues

### ❌ "Image push failed: unauthorized"

**Solution:** Images push to your repository automatically. Make sure:
1. You're pushing to your fork (not the original repo)
2. GitHub Actions has package write permissions (automatic)

### ❌ "Tests failed in CI but pass locally"

**Solution:**
```bash
# Ensure dependencies are up to date
pip install -r requirements.txt
npm install

# Check environment variables
# CI uses demo API key by default

# Run tests with same database
docker compose up -d db
pytest
```

### ❌ "Docker build takes too long"

**Solution:** Builds are cached! First build is slow, subsequent builds are fast.
- Layer caching is automatic
- GitHub Actions cache is enabled
- Builds reuse unchanged layers

## 🎯 Workflow Badges

Add to your README.md:

```markdown
![CI](https://github.com/YOUR_USERNAME/investory/workflows/CI%2FCD%20Pipeline/badge.svg)
![Docker Build](https://github.com/YOUR_USERNAME/investory/workflows/Build%20and%20Push%20Docker%20Images/badge.svg)
```

Replace `YOUR_USERNAME` with your GitHub username.

## 💡 Pro Tips

### Skip CI for Docs Changes
```bash
git commit -m "docs: update README [skip ci]"
```

### Re-run Failed Workflows
1. Go to Actions tab
2. Click on failed run
3. Click "Re-run jobs" → "Re-run failed jobs"

### Local Testing with Act
```bash
# Install act
brew install act

# Run workflow locally
act -j test-backend

# Faster: skip pulls
act -j test-backend --pull=false
```

### Speed Up Builds
1. Use `.dockerignore` (already configured)
2. Order Dockerfile commands from least to most frequently changed
3. Use multi-stage builds (already implemented)

## 🔐 Security

### Secrets (Optional)

Add in Settings → Secrets → Actions:

```yaml
# For code quality
SONAR_TOKEN: your_sonarcloud_token

# For coverage reporting  
CODECOV_TOKEN: your_codecov_token

# For release notifications
SLACK_WEBHOOK_URL: your_slack_webhook
```

### Dependabot

Automatically enabled! Creates PRs for:
- Python dependencies (weekly)
- npm dependencies (weekly)
- Docker base images (weekly)
- GitHub Actions (weekly)

## 📈 Monitoring

### View Workflow History
```bash
# Using GitHub CLI
gh run list --workflow=ci.yml --limit 10

# View specific workflow
gh run view --workflow=docker-build.yml
```

### Workflow Status
Check the Actions tab for:
- ✅ Passing workflows (green)
- ❌ Failed workflows (red)
- 🟡 In progress (yellow)

## 🎓 Learning Resources

- [GitHub Actions Docs](https://docs.github.com/en/actions)
- [Docker Build Action](https://github.com/docker/build-push-action)
- [Conventional Commits](https://www.conventionalcommits.org/)

## 📞 Getting Help

1. Check [GITHUB-ACTIONS.md](docs/GITHUB-ACTIONS.md) for detailed docs
2. View workflow logs in Actions tab
3. Check GitHub Actions status: https://www.githubstatus.com/
4. Open an issue in the repository

---

**Remember:** GitHub Actions is free for public repositories with generous limits!
- 2,000 minutes/month (private repos)
- Unlimited for public repos
- 500MB package storage
