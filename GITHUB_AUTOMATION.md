# GitHub Automation

This document describes the GitHub Actions workflows and automation set up for this project.

## Overview

The project includes automated workflows for:
1. **HACS Validation** - Validates integration for HACS compatibility
2. **Code Quality** - Linting, formatting, and validation checks
3. **Release Management** - Automated release packaging
4. **Dependency Updates** - Automatic dependency updates via Dependabot

## Workflows

### 1. HACS Validation ([`.github/workflows/hacs-validation.yml`](.github/workflows/hacs-validation.yml))

**Triggers**: Push to main/master, pull requests, manual dispatch

**What it does**:
- Validates integration structure for HACS
- Checks manifest.json format
- Checks strings.json format
- Verifies all required files exist

**Status Badge**:
```markdown
[![HACS Validation](https://github.com/xlith/solax-energy-optimizer/actions/workflows/hacs-validation.yml/badge.svg)](https://github.com/xlith/solax-energy-optimizer/actions/workflows/hacs-validation.yml)
```

### 2. Code Quality ([`.github/workflows/quality.yml`](.github/workflows/quality.yml))

**Triggers**: Push to main/master, pull requests, manual dispatch

**What it does**:
- **Linting**: Runs ruff for code quality
- **Formatting**: Checks black and isort formatting
- **Syntax**: Validates Python syntax
- **Imports**: Checks import statements
- **JSON**: Validates all JSON files
- **Structure**: Verifies integration file structure
- **Manifest**: Validates required manifest fields

**Jobs**:
1. `lint` - Code style and quality
2. `validate-python` - Python syntax and imports
3. `validate-json` - JSON file validation
4. `check-structure` - File structure verification

**Status Badge**:
```markdown
[![Code Quality](https://github.com/xlith/solax-energy-optimizer/actions/workflows/quality.yml/badge.svg)](https://github.com/xlith/solax-energy-optimizer/actions/workflows/quality.yml)
```

### 3. Release ([`.github/workflows/release.yml`](.github/workflows/release.yml))

**Triggers**: Release published, manual dispatch

**What it does**:
1. Gets version from release tag
2. Updates manifest.json with version
3. Creates release archive (zip)
4. Uploads archive to GitHub release
5. Generates release notes
6. Validates release package

**Usage**:
```bash
# Create a new release
git tag v1.0.0
git push --tags

# Or use GitHub UI:
# Releases → Draft a new release → Choose tag → Publish
```

**Artifacts**:
- `solax_energy_optimizer.zip` - Ready for manual installation

### 4. Dependabot ([`.github/dependabot.yml`](.github/dependabot.yml))

**What it does**:
- Checks for GitHub Actions updates weekly
- Creates pull requests for updates
- Labels PRs appropriately

**Configuration**:
- Package ecosystem: `github-actions`
- Schedule: Weekly
- Labels: `dependencies`, `github-actions`

## Issue Templates

Located in [`.github/ISSUE_TEMPLATE/`](.github/ISSUE_TEMPLATE/):

### Bug Report ([`bug_report.yml`](.github/ISSUE_TEMPLATE/bug_report.yml))

Structured form for bug reports including:
- Description and expected behavior
- Steps to reproduce
- Log output
- Version information
- Configuration details
- Dry run mode status

### Feature Request ([`feature_request.yml`](.github/ISSUE_TEMPLATE/feature_request.yml))

Structured form for feature requests including:
- Problem description
- Proposed solution
- Alternatives considered
- Feature category
- Use case
- Implementation ideas

### Configuration ([`config.yml`](.github/ISSUE_TEMPLATE/config.yml))

Links to:
- Documentation
- Installation guide
- Development guide
- Home Assistant community

## Pull Request Template

Located at [`.github/PULL_REQUEST_TEMPLATE.md`](.github/PULL_REQUEST_TEMPLATE.md)

Includes sections for:
- Description and type of change
- Related issues
- Changes made
- Testing performed
- Checklist for contributors

## Badges

Add these badges to your README:

```markdown
[![GitHub Release](https://img.shields.io/github/v/release/xlith/solax-energy-optimizer)](https://github.com/xlith/solax-energy-optimizer/releases)
[![GitHub Activity](https://img.shields.io/github/commit-activity/y/xlith/solax-energy-optimizer)](https://github.com/xlith/solax-energy-optimizer/commits/main)
[![License](https://img.shields.io/github/license/xlith/solax-energy-optimizer)](LICENSE)
[![HACS](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)
[![HACS Validation](https://github.com/xlith/solax-energy-optimizer/actions/workflows/hacs-validation.yml/badge.svg)](https://github.com/xlith/solax-energy-optimizer/actions/workflows/hacs-validation.yml)
[![Code Quality](https://github.com/xlith/solax-energy-optimizer/actions/workflows/quality.yml/badge.svg)](https://github.com/xlith/solax-energy-optimizer/actions/workflows/quality.yml)
```

## Workflow Status

Check workflow status:
1. Go to repository on GitHub
2. Click "Actions" tab
3. View recent workflow runs
4. Click on a run to see details

## Manually Trigger Workflows

Some workflows can be triggered manually:

1. Go to Actions tab
2. Select workflow (left sidebar)
3. Click "Run workflow" dropdown
4. Choose branch
5. Click "Run workflow" button

Available for:
- HACS Validation
- Code Quality
- Release (creates test release)

## Secrets Configuration

No secrets are currently required. If you add features needing secrets:

1. Go to Settings → Secrets and variables → Actions
2. Click "New repository secret"
3. Add secret name and value
4. Reference in workflow: `${{ secrets.SECRET_NAME }}`

## Local Testing

See [LOCAL_TESTING.md](LOCAL_TESTING.md) for testing workflows locally with `act`.

## Troubleshooting

### Workflow Failed

1. Click on the failed workflow run
2. Expand the failed job
3. Review error messages
4. Fix the issue locally
5. Push fix

### HACS Validation Failed

Common issues:
- Invalid JSON syntax
- Missing required files
- Incorrect manifest fields
- Invalid hacs.json

Fix by validating JSON locally:
```bash
python3 -m json.tool custom_components/solax_energy_optimizer/manifest.json
```

### Code Quality Failed

Common issues:
- Python syntax errors
- Import errors
- Formatting issues
- Linting violations

Fix by running locally:
```bash
black custom_components/solax_energy_optimizer/
ruff check --fix custom_components/solax_energy_optimizer/
```

### Release Failed

Common issues:
- Invalid version tag format
- Missing GITHUB_TOKEN
- Permissions issue

Ensure tag format: `v1.0.0` (with 'v' prefix)

## Best Practices

1. **Always test locally first** using [LOCAL_TESTING.md](LOCAL_TESTING.md)
2. **Use semantic versioning** (MAJOR.MINOR.PATCH)
3. **Update CHANGELOG** before releasing
4. **Write clear commit messages**
5. **Keep workflows updated** (Dependabot will help)
6. **Monitor action runs** after pushing
7. **Fix CI failures promptly**

## Release Process

Automated release process:

```bash
# 1. Update version in manifest.json (automated by workflow)
# 2. Update CHANGELOG.md
git add CHANGELOG.md
git commit -m "chore: update changelog for v1.0.0"

# 3. Create and push tag
git tag v1.0.0
git push origin v1.0.0

# 4. Create GitHub release
# Go to GitHub → Releases → Draft a new release
# - Choose tag: v1.0.0
# - Title: v1.0.0
# - Description: Copy from CHANGELOG
# - Publish release

# 5. GitHub Actions will:
# - Update manifest version
# - Create release archive
# - Upload to release
# - Generate release notes
```

## Workflow Files Location

```
.github/
├── workflows/
│   ├── hacs-validation.yml   # HACS validation
│   ├── quality.yml            # Code quality checks
│   └── release.yml            # Release automation
├── ISSUE_TEMPLATE/
│   ├── bug_report.yml         # Bug report template
│   ├── feature_request.yml    # Feature request template
│   └── config.yml             # Issue config
├── PULL_REQUEST_TEMPLATE.md   # PR template
└── dependabot.yml             # Dependency updates
```

## Continuous Integration Benefits

✅ **Automated validation** on every push
✅ **Consistent code quality**
✅ **Early issue detection**
✅ **Automated releases**
✅ **Dependency management**
✅ **Documentation enforcement**
✅ **Community standards**

## Future Enhancements

Consider adding:
- Unit test runner workflow
- Integration test workflow
- Code coverage reporting
- Automated changelog generation
- Automated version bumping
- Deploy to HACS default repo (after approval)

## Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [HACS Documentation](https://hacs.xyz/)
- [Home Assistant Development](https://developers.home-assistant.io/)
- [Semantic Versioning](https://semver.org/)
