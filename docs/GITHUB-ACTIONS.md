# GitHub Actions CI/CD Documentation

This document explains the automated workflows configured for the Rule #1 Investing Platform.

## Overview

The project uses GitHub Actions for:
- **Continuous Integration (CI)** - Testing and linting on every push
- **Docker Image Building** - Automated container builds
- **Release Management** - Versioned releases with changelogs
- **Security Scanning** - Vulnerability detection
- **Dependency Updates** - Automated dependency management

## Workflows

### 1. CI/CD Pipeline (`ci.yml`)

**Triggers:**
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop`

**Jobs:**

#### Lint Backend
- Runs `flake8` for Python code quality
- Checks formatting with `black`
- Verifies import sorting with `isort`

#### Lint Frontend
- Runs ESLint for JavaScript/React code
- Checks code style consistency

#### Test Backend
- Runs pytest with coverage
- Uses PostgreSQL service container
- Uploads coverage to Codecov
- Requires tests to pass for PR merge

#### Test Frontend
- Runs npm tests
- Builds production bundle
- Verifies no build errors

#### Code Quality
- SonarCloud static analysis (optional)
- Code smell detection
- Security vulnerability scanning

#### Dependency Review
- Reviews new dependencies in PRs
- Checks for known vulnerabilities
- Flags security issues

**Configuration Required:**
```yaml
# Repository Secrets (optional)
SONAR_TOKEN: Your SonarCloud token
CODECOV_TOKEN: Your Codecov token
```

### 2. Docker Build (`docker-build.yml`)

**Triggers:**
- Push to `main` or `develop` branches
- New version tags (`v*`)
- Pull requests (build only, no push)

**Jobs:**

#### Build Backend
- Multi-stage Docker build
- Builds for `linux/amd64` and `linux/arm64`
- Caches layers for faster builds
- Pushes to GitHub Container Registry (GHCR)

#### Build Frontend
- Multi-stage Docker build
- Nginx-based production image
- Multi-architecture support
- Pushes to GHCR

#### Integration Tests
- Starts full stack with docker compose
- Tests backend health endpoint
- Tests frontend availability
- Verifies database connectivity
- Only runs on PRs

#### Security Scan
- Trivy vulnerability scanner
- Scans both backend and frontend images
- Uploads results to GitHub Security tab
- Fails on critical vulnerabilities

**Image Tags:**
- `latest` - Latest build from main branch
- `main` - Main branch builds
- `develop` - Develop branch builds
- `pr-123` - Pull request builds
- `v1.2.3` - Version tags
- `main-abc1234` - Commit SHA tags

**Accessing Images:**
```bash
# Pull latest images
docker pull ghcr.io/YOUR_USERNAME/rule1-app/backend:latest
docker pull ghcr.io/YOUR_USERNAME/rule1-app/frontend:latest

# Pull specific version
docker pull ghcr.io/YOUR_USERNAME/rule1-app/backend:v1.0.0
```

### 3. Release Workflow (`release.yml`)

**Triggers:**
- New version tags pushed (`v*`)

**Jobs:**

#### Create Release
- Generates changelog from commits and PRs
- Creates GitHub release
- Attaches release notes
- Tags release in repository

#### Build and Push Release Images
- Builds production-ready images
- Tags with version number and `latest`
- Pushes to GHCR
- Multi-architecture builds

#### Deploy Documentation
- Publishes docs to GitHub Pages
- Updates on every release

#### Notify Release
- Sends Slack notification (optional)
- Includes release notes and links

**Creating a Release:**
```bash
# Tag the release
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0

# Or use GitHub CLI
gh release create v1.0.0 --generate-notes
```

**Configuration Required:**
```yaml
# Repository Secrets (optional)
SLACK_WEBHOOK_URL: Your Slack webhook URL
```

### 4. Dependabot (`dependabot.yml`)

**Updates:**
- Python dependencies (backend) - Weekly
- npm dependencies (frontend) - Weekly
- Docker base images - Weekly
- GitHub Actions - Weekly

**Features:**
- Automatic PR creation for updates
- Grouped security updates
- Ignores major version updates for stable packages
- Automatic labels and reviewers

## Setup Instructions

### 1. Enable GitHub Actions

Actions are enabled by default for public repositories. For private repos:

1. Go to Settings → Actions → General
2. Enable "Allow all actions and reusable workflows"
3. Save

### 2. Configure Container Registry

Images are pushed to GitHub Container Registry (GHCR):

1. Go to Settings → Packages
2. Enable "Improved container support"
3. Set package visibility (public/private)

### 3. Set Up Secrets

Add these secrets in Settings → Secrets → Actions:

```yaml
# Optional but recommended
SONAR_TOKEN: xxx        # For code quality analysis
CODECOV_TOKEN: xxx      # For coverage reporting
SLACK_WEBHOOK_URL: xxx  # For release notifications
```

### 4. Configure Branch Protection

Recommended settings for `main` branch:

1. Go to Settings → Branches → Branch protection rules
2. Add rule for `main`
3. Enable:
   - ✅ Require pull request before merging
   - ✅ Require status checks to pass
     - `lint-backend`
     - `lint-frontend`
     - `test-backend`
     - `test-frontend`
   - ✅ Require branches to be up to date
   - ✅ Require conversation resolution

### 5. Enable Dependabot Alerts

1. Go to Settings → Security → Dependabot
2. Enable:
   - ✅ Dependabot alerts
   - ✅ Dependabot security updates
   - ✅ Dependabot version updates

## Using in Your Fork

### 1. Update Repository References

Replace `${{ github.repository }}` references with your repo:

```yaml
# In docker-build.yml
env:
  IMAGE_NAME_BACKEND: YOUR_USERNAME/rule1-app/backend
  IMAGE_NAME_FRONTEND: YOUR_USERNAME/rule1-app/frontend
```

### 2. Customize Workflows

Edit workflow files in `.github/workflows/` to match your needs:

```yaml
# Change triggers
on:
  push:
    branches: [ main, develop, staging ]  # Add your branches

# Change platforms
platforms: linux/amd64  # Remove arm64 if not needed

# Adjust caching
cache-from: type=gha  # Or use type=registry
```

### 3. Test Locally

Test workflows locally using [act](https://github.com/nektos/act):

```bash
# Install act
brew install act  # macOS
# or
curl https://raw.githubusercontent.com/nektos/act/master/install.sh | sudo bash

# Run CI workflow
act -j test-backend

# Run with secrets
act -j build-backend --secret-file .env.secrets
```

## Workflow Status Badges

Add these to your README.md:

```markdown
![CI](https://github.com/YOUR_USERNAME/rule1-app/workflows/CI%2FCD%20Pipeline/badge.svg)
![Docker](https://github.com/YOUR_USERNAME/rule1-app/workflows/Build%20and%20Push%20Docker%20Images/badge.svg)
![Release](https://github.com/YOUR_USERNAME/rule1-app/workflows/Release/badge.svg)
```

## Monitoring Workflows

### View Workflow Runs
1. Go to Actions tab
2. Select workflow
3. View run details and logs

### Debugging Failed Runs
```bash
# Download logs
gh run download RUN_ID

# View logs in real-time
gh run view RUN_ID --log

# Re-run failed jobs
gh run rerun RUN_ID --failed
```

## Best Practices

### Commit Messages
Use conventional commits for automatic changelog generation:

```bash
feat: add new analysis endpoint
fix: resolve database connection issue
docs: update API documentation
chore: update dependencies
test: add integration tests
```

### Versioning
Follow semantic versioning:

- `v1.0.0` - Major release (breaking changes)
- `v1.1.0` - Minor release (new features)
- `v1.1.1` - Patch release (bug fixes)

### Pull Requests
- Keep PRs focused and small
- Ensure all checks pass before requesting review
- Add descriptive PR descriptions
- Link related issues

### Security
- Never commit secrets or API keys
- Use GitHub Secrets for sensitive data
- Regularly review Dependabot alerts
- Monitor security scan results

## Troubleshooting

### Docker Build Fails

**Problem:** "buildx failed with: ERROR: failed to solve"

**Solution:**
```yaml
# Add timeout
timeout-minutes: 30

# Clear cache
cache-to: type=gha,mode=min  # Reduce cache

# Or build without cache
cache-from: type=local  # Disable GitHub cache
```

### Tests Fail in CI

**Problem:** Tests pass locally but fail in CI

**Solution:**
- Check environment variables
- Verify service containers are healthy
- Add wait time for services to start
- Check timezone/locale differences

### Rate Limiting

**Problem:** "API rate limit exceeded"

**Solution:**
```yaml
# Add token for higher limits
- uses: actions/checkout@v4
  with:
    token: ${{ secrets.GITHUB_TOKEN }}

# Or use cache
- uses: actions/cache@v3
```

## Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Docker Build Push Action](https://github.com/docker/build-push-action)
- [Dependabot Documentation](https://docs.github.com/en/code-security/dependabot)
- [GitHub Container Registry](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry)

## Support

For issues with workflows:
1. Check workflow logs in Actions tab
2. Review this documentation
3. Check GitHub Actions status page
4. Open an issue in the repository
