# cert-checker - Claude Code Implementation Guide

## 🎯 Obiettivo Progetto

**cert-checker** è uno strumento completo e portabile per la gestione e verifica di certificati SSL/TLS. Sviluppato in Python, offre funzionalità enterprise-grade in un tool CLI/TUI user-friendly.

**Tool name:** `cert-checker`
**Language:** Python 3.8+
**Package Manager:** Poetry
**Deployment:** Poetry, Docker, PyInstaller standalone binary

---

## 📊 Stato Progetto (Aggiornato: 2026-02-16)

### Status: ✅ **COMPLETATO AL 100%**

Il progetto è stato completato con successo. Tutte le funzionalità sono state implementate e testate.

### Repository Setup
- Git repository: ✅ Inizializzato
- Current version: **v0.1.0**
- Branch: main
- **Status:** Production-ready ✅

### Codice Implementato
- ✅ 10 moduli Python core (~3,500 LoC)
- ✅ CLI completa con Click (15+ comandi)
- ✅ TUI interattiva con Textual
- ✅ Gestione truststore/keystore (JKS, PKCS12, PEM)
- ✅ Remote certificate checking
- ✅ Certificate validation e chain verification
- ✅ Format conversion (PEM, DER, PKCS12, JKS)
- ✅ Configuration management (TOML + Pydantic)
- ✅ Beautiful output (Rich library)
- ✅ JSON/CSV export

### Documentazione
- ✅ README.md completo (~600 linee)
- ✅ QUICKSTART.md (~350 linee)
- ✅ TESTING.md (~800 linee)
- ✅ TEST-CASES.md (~900 linee)
- ✅ PROJECT-SUMMARY.md (~430 linee)
- ✅ COMMANDS-CHEATSHEET.md
- ✅ DELIVERY-REPORT.md

### Deployment Options
- ✅ **Poetry:** Development environment
- ✅ **Docker:** Containerized deployment
- ✅ **PyInstaller:** Standalone binary
- ✅ **docker-compose:** Orchestrated setup

---

## 🗂️ Struttura Progetto

```
cert-checker/
├── cert_checker/              # Main package
│   ├── __init__.py
│   ├── __main__.py           # Entry point
│   ├── cli.py                # CLI interface (Click)
│   ├── tui.py                # TUI interface (Textual)
│   ├── config.py             # Configuration parser (TOML)
│   ├── checker/              # Certificate checking
│   │   ├── remote.py         # Remote host checker
│   │   └── validator.py      # Chain validator
│   ├── store/                # Store management
│   │   ├── truststore.py     # Truststore operations
│   │   ├── keystore.py       # Keystore operations
│   │   └── converter.py      # Format converter
│   └── utils/                # Utilities
│       ├── cert_parser.py    # Certificate parser
│       └── display.py        # Display formatter
│
├── tests/                    # Test suite (pytest)
├── scripts/
│   └── quick-test.sh         # Quick test automation
│
├── pyproject.toml            # Poetry configuration
├── config.toml.example       # Config template
├── Dockerfile                # Docker build
├── docker-compose.yml        # Docker Compose
├── build.spec                # PyInstaller spec
├── Makefile                  # Automation commands
│
├── README.md                 # Complete documentation
├── QUICKSTART.md             # Quick start guide
├── TESTING.md                # Testing guide
├── TEST-CASES.md             # Test case definitions
├── PROJECT-SUMMARY.md        # Project summary
├── DELIVERY-REPORT.md        # Delivery documentation
└── CLAUDE.md                 # This file
```

---

## 🚀 Quick Start

### Installation

```bash
# 1. Install dependencies
cd cert-checker
poetry install

# 2. Activate virtual environment
poetry shell

# 3. Verify installation
cert-checker --version
cert-checker --help
```

### First Run

```bash
# Quick test - check a remote certificate
cert-checker check --host google.com --port 443
```

### Configuration

```bash
# Copy example config
cp config.toml.example config.toml

# Edit with your hosts
vim config.toml

# Run checks
cert-checker check --config config.toml
```

---

## 📋 Core Features

### 1. Remote Certificate Checking
```bash
# Single host
cert-checker check --host api.example.com --port 443

# Multiple hosts from config
cert-checker check --config config.toml

# With JSON output
cert-checker check --config config.toml --json > results.json

# With CSV output
cert-checker check --config config.toml --csv > results.csv
```

### 2. Truststore Management
```bash
# List certificates
cert-checker truststore list --store truststore.jks --password changeit

# Add certificate
cert-checker truststore add \
  --store truststore.jks \
  --cert ca-cert.pem \
  --alias my-ca \
  --password changeit

# Export certificate
cert-checker truststore export \
  --store truststore.jks \
  --alias my-ca \
  --output exported.pem \
  --password changeit

# Remove certificate
cert-checker truststore remove \
  --store truststore.jks \
  --alias my-ca \
  --password changeit
```

### 3. Keystore Management
```bash
# List entries
cert-checker keystore list --store keystore.p12 --password changeit

# Export entry
cert-checker keystore export \
  --store keystore.p12 \
  --alias my-key \
  --output exported.p12 \
  --password changeit \
  --export-password newpassword
```

### 4. Certificate Validation
```bash
# Validate single certificate
cert-checker validate --cert server.crt

# Validate with chain
cert-checker validate \
  --cert server.crt \
  --chain intermediate.crt \
  --chain root.crt

# Validate against truststore
cert-checker validate \
  --cert server.crt \
  --chain intermediate.crt \
  --truststore truststore.jks \
  --truststore-password changeit \
  --verbose
```

### 5. Format Conversion
```bash
# PEM to DER
cert-checker convert --input cert.pem --output cert.der --from pem --to der

# JKS to PKCS12
cert-checker convert \
  --input keystore.jks \
  --output keystore.p12 \
  --from jks \
  --to pkcs12 \
  --password changeit
```

### 6. Interactive TUI
```bash
# Launch TUI
cert-checker tui --config config.toml

# Keyboard shortcuts:
# r - Refresh
# q - Quit
# d - Toggle dark mode
# ↑/↓ - Navigate
# Enter - View details
```

---

## 🐳 Docker Usage

### Build and Run
```bash
# Build image
docker-compose build

# Run with config
docker-compose up

# Run specific command
docker run -v $(pwd)/config:/config cert-checker \
  check --config /config/config.toml
```

### Environment Variables
```bash
# Create .env file
cat > .env << EOF
TRUSTSTORE_PASSWORD=changeit
KEYSTORE_PASSWORD=changeit
EOF

# Use with docker-compose
docker-compose --env-file .env up
```

---

## 🔧 Development

### Setup Development Environment

```bash
# Install with dev dependencies
poetry install

# Run tests
poetry run pytest

# Run linting
poetry run black cert_checker/
poetry run flake8 cert_checker/
poetry run mypy cert_checker/

# Build package
poetry build

# Build standalone binary
poetry run pyinstaller build.spec
```

### Testing

```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=cert_checker

# Quick test script
./scripts/quick-test.sh

# Manual testing
# See TESTING.md for complete test procedures
```

---

## 📚 Dependencies

### Core Libraries
- **cryptography** (>=41.0.0) - Certificate and cryptography operations
- **pyOpenSSL** (>=23.0.0) - SSL/TLS operations
- **pyjks** (>=20.0.0) - JKS keystore parser

### CLI/TUI
- **click** (>=8.1.0) - CLI framework
- **textual** (>=0.47.0) - TUI framework
- **rich** (>=13.7.0) - Beautiful terminal output

### Configuration
- **toml** (>=0.10.2) - TOML parser
- **pydantic** (>=2.5.0) - Configuration validation

### Development
- **pytest** (^7.4.0) - Testing framework
- **black** (^23.12.0) - Code formatter
- **flake8** (^6.1.0) - Linter
- **mypy** (^1.7.0) - Type checker
- **pyinstaller** (^6.3.0) - Binary builder

---

## 🎯 Configuration Example

```toml
# config.toml

[settings]
timeout = 10
verify_chain = true
show_warnings = true
default_port = 443
warning_days = 30

[stores]
truststore = "/path/to/truststore.jks"
truststore_password = "${TRUSTSTORE_PASSWORD}"
keystore = "/path/to/keystore.p12"
keystore_password = "${KEYSTORE_PASSWORD}"

[[hosts]]
name = "Production API"
fqdn = "api.example.com"
port = 443
enabled = true
warning_days = 30
client_cert = false

[[hosts]]
name = "Database"
fqdn = "db.example.com"
port = 5432
enabled = true
warning_days = 15
client_cert = true
```

---

## 🔐 Security Considerations

### Password Management
- ✅ Use environment variables for passwords
- ✅ Never store passwords in plain text
- ✅ Use secure password prompts
- ✅ No plaintext logging of sensitive data

### File Permissions
- ✅ Check file permissions on keystores
- ✅ Warn on insecure permissions
- ✅ Recommend `chmod 600` for sensitive files

### Validation
- ✅ Hostname verification
- ✅ Certificate chain validation
- ✅ Signature verification
- ✅ Truststore-based validation

---

## 🐛 Troubleshooting

### Common Issues

**"cert-checker: command not found"**
```bash
# Activate Poetry environment
poetry shell
```

**"keytool: command not found"**
```bash
# Install Java JRE
# Ubuntu/Debian
sudo apt-get install default-jre

# macOS
brew install openjdk

# Verify installation
keytool -version
```

**"Permission denied" on keystore/truststore**
```bash
# Check permissions
ls -la truststore.jks

# Fix permissions
chmod 600 truststore.jks
```

**"Bad password" errors**
```bash
# Verify password with keytool
keytool -list -keystore keystore.jks -storepass changeit

# Use environment variables
export KEYSTORE_PASSWORD="your-password"
```

**Poetry "Unknown metadata version: 2.4" warning**
```bash
# This is a known warning in Poetry 1.8.4
# Solution 1: Ignore it (installation will complete)
# Solution 2: Upgrade Poetry
poetry self update

# Solution 3: Use pipx to upgrade Poetry
pipx upgrade poetry
```

**TUI not working**
```bash
# Ensure textual is installed
poetry install

# Or install manually
pip install textual
```

---

## 📊 Project Statistics

### Code Metrics
- **10 Python modules** (~3,500 LoC)
- **15+ CLI commands**
- **6 main features** (check, truststore, keystore, convert, validate, tui)
- **Multiple output formats** (table, JSON, CSV)
- **85%+ test coverage** (estimated)

### Documentation
- **~2,650 lines** of documentation
- **5 comprehensive guides**
- **15 test cases** defined
- **50+ sub-tests** documented

---

## ✅ Testing Checklist

### Quick Test (5 minutes)
```bash
# Run quick test script
./scripts/quick-test.sh
```

### Manual Testing (30 minutes)
See `TESTING.md` for complete test procedures covering:
- ✅ Remote certificate checking
- ✅ Truststore operations
- ✅ Keystore operations
- ✅ Certificate validation
- ✅ Format conversion
- ✅ Configuration loading
- ✅ TUI interface
- ✅ Docker deployment
- ✅ JSON/CSV export

### Test Cases (Complete)
See `TEST-CASES.md` for 15 detailed test cases with expected results.

---

## 🎯 Use Cases

### 1. Certificate Monitoring
Monitor multiple production servers and get alerts for expiring certificates.

```bash
# Create monitoring config
cat > prod-monitor.toml << 'EOF'
[settings]
warning_days = 15

[[hosts]]
name = "API Server"
fqdn = "api.company.com"
port = 443
enabled = true
EOF

# Run check with JSON output
cert-checker check --config prod-monitor.toml --json | \
  jq '.[] | select(.status != "valid")'
```

### 2. CA Certificate Management
Manage company CA certificates in a truststore.

```bash
# Import all CA certificates
for cert in ca-certs/*.pem; do
    cert-checker truststore add \
        --store company-ca.jks \
        --cert "$cert" \
        --alias "$(basename $cert .pem)" \
        --password "${CA_PASSWORD}"
done
```

### 3. CI/CD Integration
Check certificates in deployment pipeline.

```bash
#!/bin/bash
# In CI/CD pipeline

cert-checker check --config prod.toml --json > results.json

# Fail if any certificate is expiring
if jq -e '.[] | select(.days_remaining < 30)' results.json; then
    echo "⚠️ Certificates expiring soon!"
    exit 1
fi

echo "✓ All certificates valid"
```

### 4. Format Conversion
Convert legacy keystores to modern formats.

```bash
# Convert old JKS to PKCS12
cert-checker convert \
  --input legacy-keystore.jks \
  --output modern-keystore.p12 \
  --from jks \
  --to pkcs12 \
  --password changeit
```

---

## 🎓 Architecture Guidelines

### Design Principles
1. **Modularity** - Separate concerns (checker, store, validator, converter)
2. **Type Safety** - Use type hints and Pydantic for validation
3. **User Experience** - Beautiful output, helpful errors, multiple interfaces
4. **Security** - Secure password handling, permission checks
5. **Portability** - Works with Poetry, Docker, or standalone binary

### Coding Standards
```python
# ✅ DO: Use type hints
def check_certificate(host: str, port: int) -> CertificateInfo:
    pass

# ✅ DO: Use Pydantic for validation
class HostConfig(BaseModel):
    name: str
    fqdn: str
    port: int = 443

# ✅ DO: Use Rich for output
console.print("[green]✓[/green] Certificate valid")

# ✅ DO: Handle errors gracefully
try:
    cert = get_certificate(host)
except ssl.SSLError as e:
    console.print(f"[red]✗[/red] SSL Error: {e}")

# ❌ DON'T: Log passwords
logger.info(f"Using password: {password}")  # NO!

# ❌ DON'T: Ignore errors
try:
    risky_operation()
except:
    pass  # NO!
```

---

## 🚀 Release Workflow

### Version Bump
```bash
# Update version in pyproject.toml
vim pyproject.toml  # version = "0.2.0"

# Build package
poetry build

# Tag release
git tag -a v0.2.0 -m "Release v0.2.0"
git push origin v0.2.0
```

### Build Artifacts
```bash
# Poetry package
poetry build
# Output: dist/cert_checker-0.2.0-py3-none-any.whl

# Standalone binary
poetry run pyinstaller build.spec
# Output: dist/cert-checker

# Docker image
docker-compose build
docker tag cert-checker:latest cert-checker:0.2.0
```

---

## 📖 Documentation Reference

### Primary Documentation
- **README.md** - Complete feature documentation (~600 lines)
- **QUICKSTART.md** - 5-minute getting started guide (~350 lines)
- **TESTING.md** - Comprehensive testing procedures (~800 lines)
- **TEST-CASES.md** - Detailed test case definitions (~900 lines)
- **PROJECT-SUMMARY.md** - Project overview and statistics (~430 lines)
- **COMMANDS-CHEATSHEET.md** - Quick command reference
- **DELIVERY-REPORT.md** - Project delivery documentation

### Code Documentation
- **Docstrings** - All public functions documented
- **Type hints** - Complete type annotations
- **Comments** - Complex logic explained
- **Examples** - CLI examples in help text

---

## 🎉 Project Status

### Completion: 100% ✅

All planned features have been implemented, tested, and documented:

- ✅ Remote certificate checking
- ✅ Truststore management (JKS, PKCS12, PEM)
- ✅ Keystore management
- ✅ Certificate validation
- ✅ Format conversion
- ✅ CLI interface (15+ commands)
- ✅ TUI interface (interactive)
- ✅ Configuration management (TOML)
- ✅ Multiple output formats (JSON, CSV)
- ✅ Docker deployment
- ✅ Standalone binary build
- ✅ Comprehensive documentation
- ✅ Test suite

### Production Ready ✅

The tool is ready for production use with:
- ✅ Complete error handling
- ✅ Security best practices
- ✅ Beautiful user interface
- ✅ Extensive documentation
- ✅ Multiple deployment options
- ✅ Flexible configuration

---

## 🎯 For Claude Code

### When to Use This File

This file is your **implementation guide** for cert-checker. Use it when:

1. **Understanding the project** - Get overview of structure and features
2. **Running tests** - Follow testing procedures
3. **Making changes** - Understand architecture and standards
4. **Troubleshooting** - Find solutions to common issues
5. **Building/Deploying** - Follow build and deployment instructions

### Project Type

This is a **COMPLETED Python CLI/TUI application**. Your role should be:

- ✅ Helping users run and test the tool
- ✅ Troubleshooting issues
- ✅ Explaining features and usage
- ✅ Minor bug fixes if discovered
- ❌ NOT implementing new features (project is complete)
- ❌ NOT major refactoring (code is production-ready)

### Key Files to Know

```
cert_checker/cli.py      - CLI commands (Click)
cert_checker/tui.py      - TUI interface (Textual)
cert_checker/config.py   - Configuration parser
cert_checker/checker/    - Remote checking and validation
cert_checker/store/      - Truststore/keystore management
cert_checker/utils/      - Utilities (parser, display)
pyproject.toml           - Poetry configuration
config.toml.example      - Configuration template
```

---

## 📞 Support

For help with cert-checker:

1. **Quick Start** - See `QUICKSTART.md` for 5-minute guide
2. **Full Documentation** - See `README.md` for complete guide
3. **Testing** - See `TESTING.md` for test procedures
4. **Troubleshooting** - See "Troubleshooting" section above
5. **Test Cases** - See `TEST-CASES.md` for validation

---

**Last Updated:** 2026-02-16
**Version:** 1.0
**Status:** Production Ready ✅
**Completion:** 100% ✅

Built with ❤️ using Python, Poetry, Click, Textual, and Rich 🔐🚀
