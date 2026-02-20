#!/usr/bin/env bash
# Usage:
#   ./scripts/release.sh patch   # 0.0.1 → 0.0.2
#   ./scripts/release.sh minor   # 0.0.2 → 0.1.0
#   ./scripts/release.sh major   # 0.1.0 → 1.0.0
#   ./scripts/release.sh 1.2.3   # explicit version

set -euo pipefail

MANIFEST="custom_components/solax_energy_optimizer/manifest.json"
PYPROJECT="pyproject.toml"
CHANGELOG="CHANGELOG.md"

# ── Validate working tree ──────────────────────────────────────────────────────
if ! git diff --quiet || ! git diff --staged --quiet; then
  echo "Error: working tree has uncommitted changes. Commit or stash them first." >&2
  exit 1
fi

# ── Read current version from manifest.json ───────────────────────────────────
CURRENT=$(grep '"version"' "$MANIFEST" | sed 's/.*"version": "\(.*\)".*/\1/')
IFS='.' read -r MAJOR MINOR PATCH <<< "$CURRENT"

BUMP="${1:-patch}"

case "$BUMP" in
  major)
    MAJOR=$((MAJOR + 1)); MINOR=0; PATCH=0 ;;
  minor)
    MAJOR=$MAJOR; MINOR=$((MINOR + 1)); PATCH=0 ;;
  patch)
    MAJOR=$MAJOR; MINOR=$MINOR; PATCH=$((PATCH + 1)) ;;
  [0-9]*.[0-9]*.[0-9]*)
    IFS='.' read -r MAJOR MINOR PATCH <<< "$BUMP" ;;
  *)
    echo "Usage: $0 [major|minor|patch|X.Y.Z]" >&2; exit 1 ;;
esac

VERSION="${MAJOR}.${MINOR}.${PATCH}"
TAG="v${VERSION}"

echo "Bumping ${CURRENT} → ${VERSION}"

# ── Update manifest.json ──────────────────────────────────────────────────────
sed -i.bak "s/\"version\": \".*\"/\"version\": \"${VERSION}\"/" "$MANIFEST"
rm -f "${MANIFEST}.bak"

# ── Update pyproject.toml ─────────────────────────────────────────────────────
sed -i.bak "s/^version = \".*\"/version = \"${VERSION}\"/" "$PYPROJECT"
rm -f "${PYPROJECT}.bak"

# ── Update CHANGELOG.md ───────────────────────────────────────────────────────
TODAY=$(date +%Y-%m-%d)
# Replace [Unreleased] heading with the new version + date, then re-insert a blank [Unreleased]
UNRELEASED_BLOCK="## [Unreleased]\n\n### Added\n\n### Changed\n\n### Fixed\n\n### Security\n"
sed -i.bak \
  "s|## \[Unreleased\]|${UNRELEASED_BLOCK}\n## [${VERSION}] - ${TODAY}|" \
  "$CHANGELOG"
rm -f "${CHANGELOG}.bak"

# Update comparison links at the bottom
if grep -q "\[Unreleased\]:" "$CHANGELOG"; then
  sed -i.bak \
    "s|\[Unreleased\]: \(.*\)/compare/v.*\.\.\.HEAD|\[Unreleased\]: \1/compare/${TAG}...HEAD\n[${VERSION}]: \1/compare/v${CURRENT}...${TAG}|" \
    "$CHANGELOG"
  rm -f "${CHANGELOG}.bak"
fi

# ── Commit & tag ──────────────────────────────────────────────────────────────
git add "$MANIFEST" "$PYPROJECT" "$CHANGELOG"
git commit -m "chore: release ${TAG}"
git tag -a "$TAG" -m "Release ${TAG}"

echo ""
echo "Created commit and tag ${TAG}."
echo "Push with:  git push && git push origin ${TAG}"
