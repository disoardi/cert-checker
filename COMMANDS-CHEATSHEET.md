# cert-checker - Commands Cheatsheet

Riferimento rapido ai comandi più usati.

## 🚀 Setup Iniziale

```bash
# Install con Poetry
poetry install
poetry shell

# Quick test
cert-checker --version
cert-checker --help
```

## 🔍 Remote Certificate Checking

### Check Singolo
```bash
# Basic check
cert-checker check --host google.com

# Con porta custom
cert-checker check --host db.example.com --port 5432

# Con timeout custom
cert-checker check --host slow-server.com --timeout 30

# Verbose output
cert-checker check --host github.com -v

# Warning threshold personalizzato (15 giorni)
cert-checker check --host example.com --warning-days 15
```

### Check Multipli
```bash
# Da config file
cert-checker check --config config.toml

# Con verbose
cert-checker check --config config.toml -v

# Export JSON
cert-checker check --config config.toml --json

# Export CSV
cert-checker check --config config.toml --csv

# Save to file
cert-checker check --config config.toml --json > report.json
cert-checker check --config config.toml --csv > report.csv
```

## 📦 Truststore Commands

### List Certificates
```bash
# JKS truststore
cert-checker truststore list \
  --store truststore.jks \
  --password changeit

# PKCS12 truststore
cert-checker truststore list \
  --store truststore.p12 \
  --password changeit \
  --format pkcs12

# PEM directory
cert-checker truststore list \
  --store /path/to/certs/ \
  --format pem
```

### Add Certificate
```bash
# Add to JKS
cert-checker truststore add \
  --store truststore.jks \
  --cert ca-cert.pem \
  --alias my-ca \
  --password changeit

# Create new truststore
cert-checker truststore add \
  --store new-truststore.jks \
  --cert ca-cert.pem \
  --alias root-ca \
  --password changeit \
  --format jks
```

### Export Certificate
```bash
# Export as PEM
cert-checker truststore export \
  --store truststore.jks \
  --alias my-ca \
  --output exported.pem \
  --password changeit

# Export as DER
cert-checker truststore export \
  --store truststore.jks \
  --alias my-ca \
  --output exported.der \
  --password changeit \
  --output-format der
```

### Remove Certificate
```bash
cert-checker truststore remove \
  --store truststore.jks \
  --alias old-ca \
  --password changeit
```

## 🔑 Keystore Commands

### List Entries
```bash
# PKCS12 keystore
cert-checker keystore list \
  --store keystore.p12 \
  --password changeit

# JKS keystore
cert-checker keystore list \
  --store keystore.jks \
  --password changeit \
  --format jks
```

### Export Entry
```bash
# Export as PKCS12
cert-checker keystore export \
  --store keystore.p12 \
  --alias my-key \
  --output exported.p12 \
  --password changeit \
  --export-password newpass

# Export as PEM files
cert-checker keystore export \
  --store keystore.p12 \
  --alias my-key \
  --output exported \
  --password changeit \
  --output-format pem
# Creates: exported_key.pem, exported_cert.pem, exported_chain.pem
```

## 🔄 Format Conversion

### PEM ↔ DER
```bash
# PEM to DER
cert-checker convert \
  --input cert.pem \
  --output cert.der \
  --from pem \
  --to der

# DER to PEM
cert-checker convert \
  --input cert.der \
  --output cert.pem \
  --from der \
  --to pem
```

### JKS ↔ PKCS12
```bash
# JKS to PKCS12
cert-checker convert \
  --input keystore.jks \
  --output keystore.p12 \
  --from jks \
  --to pkcs12 \
  --password changeit

# PKCS12 to JKS
cert-checker convert \
  --input keystore.p12 \
  --output keystore.jks \
  --from pkcs12 \
  --to jks \
  --password changeit
```

## ✅ Certificate Validation

### Single Certificate
```bash
# Basic validation
cert-checker validate --cert server.crt

# Verbose output
cert-checker validate --cert server.crt --verbose

# Self-signed certificate
cert-checker validate --cert self-signed.crt -v
```

### Certificate Chain
```bash
# Validate with intermediate
cert-checker validate \
  --cert server.crt \
  --chain intermediate.crt

# Full chain
cert-checker validate \
  --cert server.crt \
  --chain intermediate.crt \
  --chain root.crt \
  --verbose
```

### Validate Against Truststore
```bash
cert-checker validate \
  --cert server.crt \
  --chain intermediate.crt \
  --truststore truststore.jks \
  --truststore-password changeit \
  --verbose
```

## 🖥️ TUI (Interactive)

```bash
# Launch TUI
cert-checker tui

# With config
cert-checker tui --config config.toml

# Keyboard shortcuts:
# r - Refresh
# ↑/↓ - Navigate
# Tab - Switch tabs
# d - Toggle dark mode
# q - Quit
```

## 🐳 Docker Commands

### Build & Run
```bash
# Build image
docker-compose build

# Run default command
docker-compose up

# Run in background
docker-compose up -d

# View logs
docker-compose logs -f
```

### Run Specific Commands
```bash
# Check single host
docker run --rm cert-checker \
  check --host google.com --port 443

# Check with config
docker run --rm \
  -v $(pwd)/config:/config \
  cert-checker \
  check --config /config/config.toml

# List truststore
docker run --rm \
  -v $(pwd)/certs:/certs \
  cert-checker \
  truststore list --store /certs/truststore.jks --password changeit

# TUI in Docker
docker run --rm -it \
  -v $(pwd)/config:/config \
  cert-checker \
  tui --config /config/config.toml
```

## 🛠️ Makefile Shortcuts

```bash
# Show available commands
make help

# Install dependencies
make install

# Run tests
make test

# Lint and format
make lint
make format

# Quick test Google
make check-google

# Launch TUI
make tui

# Build Docker
make docker-build
make docker-run

# Clean artifacts
make clean

# Build standalone binary
make build-binary
```

## 📋 Configuration Examples

### Minimal Config
```toml
[settings]
timeout = 10

[[hosts]]
name = "Test Host"
fqdn = "google.com"
port = 443
enabled = true
```

### Production Config
```toml
[settings]
timeout = 10
verify_chain = true
warning_days = 15

[stores]
truststore = "/etc/ssl/truststore.jks"
truststore_password = "${TRUSTSTORE_PASS}"

[[hosts]]
name = "Production API"
fqdn = "api.company.com"
port = 443
enabled = true
warning_days = 15

[[hosts]]
name = "Database"
fqdn = "db.company.com"
port = 5432
enabled = true
client_cert = true
```

### With Environment Variables
```bash
# Set password in environment
export TRUSTSTORE_PASS="secret123"
export KEYSTORE_PASS="secret456"

# Use in config.toml
# truststore_password = "${TRUSTSTORE_PASS}"
```

## 🔧 OpenSSL Integration

### Generate Test Certificate
```bash
# Self-signed certificate
openssl req -x509 -newkey rsa:2048 -nodes \
  -keyout key.pem -out cert.pem -days 365 \
  -subj "/CN=test.example.com/O=Test Org/C=IT"

# Then validate with cert-checker
cert-checker validate --cert cert.pem -v
```

### Download Remote Certificate
```bash
# Download from server
echo | openssl s_client -showcerts -connect google.com:443 2>/dev/null | \
  openssl x509 -outform PEM > google-cert.pem

# Validate
cert-checker validate --cert google-cert.pem -v
```

### Create PKCS12 for Testing
```bash
# Create PKCS12 from PEM
openssl pkcs12 -export \
  -in cert.pem \
  -inkey key.pem \
  -out keystore.p12 \
  -name my-key \
  -passout pass:changeit

# List with cert-checker
cert-checker keystore list \
  --store keystore.p12 \
  --password changeit
```

## 📊 Output Processing

### JSON Processing with jq
```bash
# Get only expired certificates
cert-checker check --config config.toml --json | \
  jq '.[] | select(.status == "expired")'

# Get certificates expiring in < 30 days
cert-checker check --config config.toml --json | \
  jq '.[] | select(.certificate.days_remaining < 30)'

# Extract hostnames with issues
cert-checker check --config config.toml --json | \
  jq '.[] | select(.status != "valid") | .fqdn'

# Count by status
cert-checker check --config config.toml --json | \
  jq 'group_by(.status) | map({status: .[0].status, count: length})'
```

### CSV Processing
```bash
# Import in spreadsheet-friendly format
cert-checker check --config config.toml --csv > report.csv

# Filter with awk
cert-checker check --config config.toml --csv | \
  awk -F',' '$4 == "warning" {print $1, $2}'

# Sort by days remaining
cert-checker check --config config.toml --csv | \
  tail -n +2 | sort -t',' -k8 -n
```

## 🔍 Debugging & Troubleshooting

### Verbose Output
```bash
# Maximum verbosity
cert-checker check --host example.com -vvv

# Debug mode (if implemented)
CERT_CHECKER_DEBUG=1 cert-checker check --host example.com
```

### Test Connectivity
```bash
# Quick connectivity test
timeout 5 bash -c '</dev/tcp/example.com/443' && echo "Port open"

# With openssl
openssl s_client -connect example.com:443 -servername example.com
```

### Verify Truststore Password
```bash
# Test with keytool
keytool -list -keystore truststore.jks -storepass changeit

# Test with cert-checker
cert-checker truststore list \
  --store truststore.jks \
  --password changeit
```

## 📝 Quick Scripts

### Daily Monitoring Script
```bash
#!/bin/bash
# daily-cert-check.sh

REPORT_FILE="cert-report-$(date +%Y%m%d).json"

cert-checker check --config production.toml --json > "$REPORT_FILE"

# Check for issues
if jq -e '.[] | select(.status != "valid")' "$REPORT_FILE" > /dev/null; then
    echo "⚠️  Certificate issues detected!"
    jq '.[] | select(.status != "valid")' "$REPORT_FILE"
    exit 1
else
    echo "✅ All certificates OK"
fi
```

### Bulk Certificate Import
```bash
#!/bin/bash
# import-cas.sh

TRUSTSTORE="company-truststore.jks"
PASSWORD="changeit"

for cert in ca-certs/*.pem; do
    ALIAS=$(basename "$cert" .pem)
    cert-checker truststore add \
        --store "$TRUSTSTORE" \
        --cert "$cert" \
        --alias "$ALIAS" \
        --password "$PASSWORD"
done
```

### Certificate Expiry Report
```bash
#!/bin/bash
# expiry-report.sh

cert-checker check --config production.toml --csv | \
  awk -F',' 'NR==1 || $8 < 30' | \
  column -t -s','
```

## 🎯 Common Workflows

### Workflow 1: New Certificate Authority
```bash
# 1. Add to truststore
cert-checker truststore add \
  --store truststore.jks \
  --cert new-ca.pem \
  --alias new-ca \
  --password changeit

# 2. Verify
cert-checker truststore list \
  --store truststore.jks \
  --password changeit

# 3. Validate test certificate
cert-checker validate \
  --cert server.crt \
  --truststore truststore.jks \
  --truststore-password changeit
```

### Workflow 2: Certificate Renewal Check
```bash
# 1. Check current status
cert-checker check --host api.example.com --verbose

# 2. Download new certificate
# ... (after renewal)

# 3. Validate new certificate
cert-checker validate --cert new-cert.pem -v

# 4. Monitor after deployment
cert-checker check --host api.example.com --verbose
```

### Workflow 3: Keystore Migration
```bash
# 1. List old keystore
cert-checker keystore list --store old.jks --format jks

# 2. Convert to PKCS12
cert-checker convert \
  --input old.jks \
  --output new.p12 \
  --from jks --to pkcs12 \
  --password changeit

# 3. Verify new keystore
cert-checker keystore list --store new.p12 --password changeit
```

---

## 💡 Tips & Tricks

### Tip 1: Use Environment Variables for Passwords
```bash
export CERT_CHECKER_PASSWORD="your-password"
cert-checker truststore list --store truststore.jks --password "$CERT_CHECKER_PASSWORD"
```

### Tip 2: Alias for Common Commands
```bash
# In ~/.bashrc or ~/.zshrc
alias certcheck='cert-checker check --config ~/config.toml'
alias certlist='cert-checker truststore list'
alias certtui='cert-checker tui --config ~/config.toml'
```

### Tip 3: JSON Output for Monitoring
```bash
# In cron or monitoring system
cert-checker check --config production.toml --json | \
  your-monitoring-tool --stdin
```

### Tip 4: Quick Certificate Info
```bash
# Create function in shell
certinfo() {
    cert-checker validate --cert "$1" -v | head -20
}

# Use it
certinfo server.crt
```

---

**For complete documentation, see README.md**

**For testing guide, see TESTING.md**

**For detailed test cases, see TEST-CASES.md**
