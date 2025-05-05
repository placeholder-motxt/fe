#!/bin/bash

# Path to the config file
CONFIG_FILE="app/config.py"

# Get the current branch (or the branch the PR is being merged into)
BRANCH=$(git rev-parse --abbrev-ref HEAD)
SOURCE=$1

# Read the current version from the config file
CURRENT_VERSION=$(grep -oP 'VERSION = "\K[0-9]+\.[0-9]+\.[0-9]+' "$CONFIG_FILE")

# Split the version into major, minor, and patch
IFS='.' read -r MAJOR MINOR PATCH <<< "$CURRENT_VERSION"

# Update the version based on the branch
if [[ "$SOURCE" =~ ^BUG-FIX- ]]; then
  PATCH=$((PATCH + 1))
elif [[ "$BRANCH" == "main" ]]; then
  MAJOR=$((MAJOR + 1))
  MINOR=0
  PATCH=0
elif [[ "$BRANCH" == "staging" ]]; then
  MINOR=$((MINOR + 1))
  PATCH=0
elif [[ "$BRANCH" == "dev" ]]; then
  PATCH=$((PATCH + 1))
else
  echo "Branch not recognized: $BRANCH. No version update performed."
  exit 0
fi

# Construct the new version
NEW_VERSION="$MAJOR.$MINOR.$PATCH"

# Update the version in the config file
sed -i "s/VERSION = \"$CURRENT_VERSION\"/VERSION = \"$NEW_VERSION\"/" "$CONFIG_FILE"

# Print the new version
echo "Updated version to $NEW_VERSION"
