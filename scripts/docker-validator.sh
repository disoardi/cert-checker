#!/bin/bash
# Docker Validator Script
# Detects common Docker build issues and suggests fixes

set -e

echo "🔍 Validating Dockerfile..."
echo ""

ISSUES_FOUND=0

# Check if Dockerfile exists
if [ ! -f "Dockerfile" ]; then
    echo "❌ Dockerfile not found in current directory"
    exit 1
fi

# Check 1: Version-specific Java packages
if grep -q "openjdk-[0-9]" Dockerfile; then
    ISSUES_FOUND=$((ISSUES_FOUND + 1))
    echo "⚠️  Issue #$ISSUES_FOUND: Version-specific Java detected"
    echo "   Found: $(grep "openjdk-[0-9]" Dockerfile | head -1 | xargs)"
    echo "   💡 Suggestion: Use 'default-jre-headless' instead"
    echo "   📝 Reason: Version-specific packages may not be available in all base images"
    echo ""
fi

# Check 2: Poetry in production/runtime stages
if grep -q "poetry install" Dockerfile; then
    # Check if it's NOT in a builder stage
    if ! grep -B5 "poetry install" Dockerfile | grep -q "AS builder"; then
        ISSUES_FOUND=$((ISSUES_FOUND + 1))
        echo "⚠️  Issue #$ISSUES_FOUND: Poetry detected in production stage"
        echo "   💡 Suggestion: Use pip + requirements.txt for production builds"
        echo "   📝 Reason: Poetry can cause dependency conflicts and slower builds"
        echo ""
    fi
fi

# Check 3: Deprecated Poetry flags
if grep -q "\-\-no-dev" Dockerfile; then
    ISSUES_FOUND=$((ISSUES_FOUND + 1))
    echo "⚠️  Issue #$ISSUES_FOUND: Deprecated Poetry flag '--no-dev' found"
    echo "   💡 Suggestion: Use '--only main' or migrate to pip + requirements.txt"
    echo "   📝 Reason: --no-dev is deprecated in recent Poetry versions"
    echo ""
fi

# Check 4: Multi-stage build
if ! grep -q "FROM.*AS" Dockerfile; then
    ISSUES_FOUND=$((ISSUES_FOUND + 1))
    echo "💡 Optimization #$ISSUES_FOUND: Not using multi-stage build"
    echo "   Consider: Use multi-stage build for smaller images"
    echo "   📝 Benefit: Reduces final image size by excluding build dependencies"
    echo ""
fi

# Check 5: Missing .dockerignore
if [ ! -f ".dockerignore" ]; then
    ISSUES_FOUND=$((ISSUES_FOUND + 1))
    echo "💡 Optimization #$ISSUES_FOUND: Missing .dockerignore file"
    echo "   Consider: Create .dockerignore to exclude unnecessary files"
    echo "   📝 Benefit: Faster builds, smaller context"
    echo ""
fi

# Check 6: COPY before RUN (layer optimization)
COPY_BEFORE_RUN=$(grep -n "^COPY" Dockerfile | head -1 | cut -d: -f1)
RUN_BEFORE_COPY=$(grep -n "^RUN.*install" Dockerfile | head -1 | cut -d: -f1)

if [ -n "$COPY_BEFORE_RUN" ] && [ -n "$RUN_BEFORE_COPY" ]; then
    if [ "$COPY_BEFORE_RUN" -lt "$RUN_BEFORE_COPY" ]; then
        echo "💡 Optimization: COPY happens before dependency installation"
        echo "   Consider: Install dependencies before copying code"
        echo "   📝 Benefit: Better layer caching when code changes"
        echo ""
    fi
fi

# Check 7: Hardcoded versions in apt-get
if grep -q "apt-get install.*[0-9]" Dockerfile && ! grep -q "python:" Dockerfile; then
    echo "⚠️  Warning: Hardcoded package versions detected in apt-get"
    echo "   💡 Consider: Use latest versions or pin carefully"
    echo ""
fi

# Summary
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if [ $ISSUES_FOUND -eq 0 ]; then
    echo "✅ No issues found! Dockerfile looks good."
else
    echo "📊 Found $ISSUES_FOUND potential issues/optimizations"
    echo ""
    echo "💡 Run 'docker build .' to test the build"
fi
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
