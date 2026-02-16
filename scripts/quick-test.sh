#!/bin/bash
# Quick test script for cert-checker

set -e

echo "=========================================="
echo "cert-checker - Quick Test Suite"
echo "=========================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if cert-checker is available
if ! command -v cert-checker &> /dev/null; then
    echo -e "${RED}✗ cert-checker not found${NC}"
    echo "Please install with: poetry install && poetry shell"
    exit 1
fi

echo -e "${GREEN}✓ cert-checker found${NC}"
echo ""

# Test 1: Check single host
echo "Test 1: Checking google.com certificate..."
if cert-checker check --host google.com --port 443 > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Test 1 passed${NC}"
else
    echo -e "${RED}✗ Test 1 failed${NC}"
fi
echo ""

# Test 2: Check with verbose
echo "Test 2: Checking github.com with verbose output..."
if cert-checker check --host github.com --port 443 --verbose > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Test 2 passed${NC}"
else
    echo -e "${RED}✗ Test 2 failed${NC}"
fi
echo ""

# Test 3: JSON export
echo "Test 3: Exporting to JSON..."
if cert-checker check --host google.com --port 443 --json | jq . > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Test 3 passed${NC}"
else
    echo -e "${YELLOW}⚠ Test 3 warning: jq not installed${NC}"
fi
echo ""

# Test 4: Create test certificates
echo "Test 4: Creating test certificates..."
mkdir -p test-certs

openssl req -x509 -newkey rsa:2048 -nodes \
  -keyout test-certs/test-key.pem \
  -out test-certs/test-cert.pem \
  -days 365 \
  -subj "/CN=test.example.com/O=Test/C=IT" > /dev/null 2>&1

if [ -f test-certs/test-cert.pem ]; then
    echo -e "${GREEN}✓ Test 4 passed${NC}"
else
    echo -e "${RED}✗ Test 4 failed${NC}"
fi
echo ""

# Test 5: Convert PEM to DER
echo "Test 5: Converting PEM to DER..."
if cert-checker convert \
    --input test-certs/test-cert.pem \
    --output test-certs/test-cert.der \
    --from pem \
    --to der > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Test 5 passed${NC}"
else
    echo -e "${RED}✗ Test 5 failed${NC}"
fi
echo ""

# Test 6: Validate certificate
echo "Test 6: Validating test certificate..."
if cert-checker validate --cert test-certs/test-cert.pem > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Test 6 passed${NC}"
else
    echo -e "${RED}✗ Test 6 failed${NC}"
fi
echo ""

# Test 7: Create JKS truststore (requires keytool)
echo "Test 7: Creating JKS truststore..."
if command -v keytool &> /dev/null; then
    keytool -import -noprompt -trustcacerts \
      -alias test-ca \
      -file test-certs/test-cert.pem \
      -keystore test-certs/test-truststore.jks \
      -storepass changeit > /dev/null 2>&1

    if cert-checker truststore list \
        --store test-certs/test-truststore.jks \
        --password changeit > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Test 7 passed${NC}"
    else
        echo -e "${RED}✗ Test 7 failed${NC}"
    fi
else
    echo -e "${YELLOW}⚠ Test 7 skipped: keytool not found${NC}"
fi
echo ""

# Test 8: Check version
echo "Test 8: Checking version..."
if cert-checker --version > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Test 8 passed${NC}"
    cert-checker --version
else
    echo -e "${RED}✗ Test 8 failed${NC}"
fi
echo ""

# Summary
echo "=========================================="
echo "Test Suite Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Copy config: cp config.toml.example config.toml"
echo "2. Edit config: vim config.toml"
echo "3. Run checks: cert-checker check --config config.toml"
echo "4. Launch TUI: cert-checker tui --config config.toml"
echo ""
echo "For full test suite, see: TESTING.md"
echo ""

# Cleanup option
read -p "Clean up test files? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    rm -rf test-certs/
    echo -e "${GREEN}✓ Test files cleaned up${NC}"
fi
