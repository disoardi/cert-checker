# cert-checker 🔐

**Swiss Army knife for SSL/TLS certificate management and verification**

A comprehensive, portable tool for checking, managing, and validating SSL/TLS certificates. Perfect for DevOps, SysAdmins, and Security Engineers who need to monitor certificate expiration, manage truststores/keystores, and validate certificate chains.

## Features

✅ **Remote Certificate Checking**
- Check SSL/TLS certificates on remote hosts
- Monitor expiration dates with configurable warnings
- Verify hostname matching (CN and SAN)
- Support for custom ports and timeouts
- Batch checking from configuration file

✅ **Truststore Management**
- List, add, remove, and export certificates
- Support for multiple formats: JKS, PKCS12, PEM
- Import certificates from various sources
- Validate truststore contents

✅ **Keystore Management**
- Manage private keys and certificate chains
- Export entries in various formats
- Support for JKS and PKCS12 formats
- Secure password handling

✅ **Certificate Validation**
- Validate certificate chains
- Verify signatures
- Check key usage and extended key usage
- Truststore-based validation

✅ **Format Conversion**
- Convert between PEM, DER, PKCS12, JKS
- Batch conversion support
- Preserve certificate chains

✅ **Multiple Interfaces**
- **CLI**: Full-featured command-line interface
- **TUI**: Interactive text-based user interface
- **JSON/CSV Export**: For automation and reporting

## Installation

### Using Poetry (Recommended for Development)

```bash
# Clone repository
git clone https://github.com/yourusername/cert-checker.git
cd cert-checker

# Install with Poetry
poetry install

# Activate virtual environment
poetry shell

# Run
cert-checker --help
```

### Using Docker

```bash
# Build image
docker-compose build

# Run with configuration
docker-compose up

# Or run directly
docker run -v $(pwd)/config:/config cert-checker check --config /config/config.toml
```

### Build Standalone Executable

```bash
# Using PyInstaller
poetry run pyinstaller build.spec

# The executable will be in dist/cert-checker
./dist/cert-checker --help
```

## Quick Start

### 1. Check a Remote Host

```bash
# Check single host
cert-checker check --host google.com --port 443

# With verbose output
cert-checker check --host api.example.com --verbose
```

### 2. Check Multiple Hosts from Config

```bash
# Create config file
cp config.toml.example config.toml

# Edit config.toml with your hosts
vim config.toml

# Run checks
cert-checker check --config config.toml

# Export results
cert-checker check --config config.toml --json > results.json
cert-checker check --config config.toml --csv > results.csv
```

### 3. Manage Truststore

```bash
# List certificates in truststore
cert-checker truststore list --store /path/to/truststore.jks --password changeit

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
  --output exported-cert.pem \
  --password changeit

# Remove certificate
cert-checker truststore remove \
  --store truststore.jks \
  --alias my-ca \
  --password changeit
```

### 4. Manage Keystore

```bash
# List entries in keystore
cert-checker keystore list --store keystore.p12 --password changeit

# Export entry
cert-checker keystore export \
  --store keystore.p12 \
  --alias my-key \
  --output exported.p12 \
  --password changeit \
  --export-password newpassword
```

### 5. Convert Certificate Formats

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

### 6. Validate Certificate Chain

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

### 7. Launch Interactive TUI

```bash
# Launch TUI
cert-checker tui --config config.toml

# Keyboard shortcuts:
# - r: Refresh
# - q: Quit
# - d: Toggle dark mode
# - ↑/↓: Navigate
# - Enter: View details
```

## Configuration

Create a `config.toml` file (see `config.toml.example` for full reference):

```toml
# Global settings
[settings]
timeout = 10
verify_chain = true
show_warnings = true
default_port = 443

# Stores (optional)
[stores]
truststore = "/path/to/truststore.jks"
truststore_password = "${TRUSTSTORE_PASSWORD}"
keystore = "/path/to/keystore.p12"
keystore_password = "${KEYSTORE_PASSWORD}"

# Hosts to monitor
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

### Environment Variables

Passwords can be stored in environment variables:

```bash
export TRUSTSTORE_PASSWORD="my-secret-password"
export KEYSTORE_PASSWORD="another-secret"

# Use in config.toml:
# truststore_password = "${TRUSTSTORE_PASSWORD}"
```

## CLI Commands Reference

### Global Options

```bash
cert-checker --help              # Show help
cert-checker --version           # Show version
```

### Check Certificates

```bash
cert-checker check [OPTIONS]

Options:
  -c, --config PATH          Configuration file
  -h, --host TEXT            Host FQDN
  -p, --port INTEGER         Port (default: 443)
  -t, --timeout INTEGER      Timeout (default: 10)
  -w, --warning-days INTEGER Warning threshold (default: 30)
  -v, --verbose              Verbose output
  --json                     JSON output
  --csv                      CSV output
```

### Truststore Commands

```bash
cert-checker truststore list --store PATH [OPTIONS]
cert-checker truststore add --store PATH --cert PATH --alias TEXT [OPTIONS]
cert-checker truststore remove --store PATH --alias TEXT [OPTIONS]
cert-checker truststore export --store PATH --alias TEXT --output PATH [OPTIONS]

Options:
  -s, --store PATH              Truststore path
  -p, --password TEXT           Password
  -f, --format [jks|pkcs12|pem] Format (default: jks)
```

### Keystore Commands

```bash
cert-checker keystore list --store PATH [OPTIONS]
cert-checker keystore export --store PATH --alias TEXT --output PATH [OPTIONS]

Options:
  -s, --store PATH                  Keystore path
  -a, --alias TEXT                  Entry alias
  -p, --password TEXT               Password
  --export-password TEXT            Export password
  -f, --format [jks|pkcs12]        Format (default: pkcs12)
  --output-format [pkcs12|pem]     Output format
```

### Convert Certificates

```bash
cert-checker convert --input PATH --output PATH --from FORMAT --to FORMAT [OPTIONS]

Formats: pem, der, pkcs12, jks

Options:
  -p, --password TEXT  Password (for JKS/PKCS12)
```

### Validate Certificates

```bash
cert-checker validate --cert PATH [OPTIONS]

Options:
  -c, --cert PATH             Certificate file
  --chain PATH                Chain certificate (multiple)
  -t, --truststore PATH       Truststore for validation
  --truststore-password TEXT  Truststore password
  -v, --verbose               Verbose output
```

### Launch TUI

```bash
cert-checker tui [--config PATH]
```

## Docker Usage

### Basic Usage

```bash
# Check hosts from config
docker-compose up

# Run specific command
docker run -v $(pwd)/certs:/certs cert-checker \
  truststore list --store /certs/truststore.jks
```

### Environment Variables

```bash
# Create .env file
echo "TRUSTSTORE_PASSWORD=changeit" > .env
echo "KEYSTORE_PASSWORD=changeit" >> .env

# Use with docker-compose
docker-compose --env-file .env up
```

### Interactive TUI in Docker

```bash
docker-compose run --rm cert-checker-tui
```

## Development

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

# Build
poetry build
```

### Project Structure

```
cert-checker/
├── cert_checker/
│   ├── __init__.py
│   ├── __main__.py           # Entry point
│   ├── cli.py                # CLI interface
│   ├── tui.py                # TUI interface
│   ├── config.py             # Configuration parser
│   ├── checker/
│   │   ├── remote.py         # Remote certificate checker
│   │   └── validator.py      # Certificate validator
│   ├── store/
│   │   ├── truststore.py     # Truststore manager
│   │   ├── keystore.py       # Keystore manager
│   │   └── converter.py      # Format converter
│   └── utils/
│       ├── cert_parser.py    # Certificate parser
│       └── display.py        # Display formatter
├── tests/
├── config.toml.example       # Example configuration
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
└── README.md
```

## Requirements

- Python 3.8+
- Java JRE (for JKS operations with keytool)
- Dependencies (automatically installed):
  - cryptography
  - pyOpenSSL
  - click
  - rich
  - textual
  - pydantic
  - pyjks

## Security Considerations

⚠️ **Important Security Notes:**

1. **Password Storage**: Never store passwords in plain text. Use environment variables or secure password managers.

2. **File Permissions**: Ensure keystores and truststores have appropriate file permissions (e.g., `chmod 600`).

3. **Sensitive Data**: Be careful when exporting private keys. Always use strong passwords and secure channels.

4. **Validation**: Always validate certificates against trusted CAs before accepting them.

## Troubleshooting

### Common Issues

**"keytool not found"**
```bash
# Install Java JRE
# Ubuntu/Debian
sudo apt-get install default-jre

# macOS
brew install openjdk

# Verify
keytool -version
```

**"Permission denied" on keystore/truststore**
```bash
# Check file permissions
ls -la /path/to/keystore.jks

# Fix permissions
chmod 600 /path/to/keystore.jks
```

**"Bad password" errors**
```bash
# Verify password with keytool
keytool -list -keystore keystore.jks -storepass changeit

# Use environment variables in config
export KEYSTORE_PASSWORD="your-password"
```

**TUI not working**
```bash
# Ensure textual is installed
poetry install --extras tui

# Or
pip install textual
```

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Author

Created by [Your Name]

## Acknowledgments

- Built with [cryptography](https://cryptography.io/)
- CLI powered by [Click](https://click.palletsprojects.com/)
- TUI powered by [Textual](https://textual.textualize.io/)
- Beautiful output with [Rich](https://rich.readthedocs.io/)

## Roadmap

Future enhancements:

- [ ] OCSP stapling support
- [ ] Certificate Transparency monitoring
- [ ] HTML/PDF report generation
- [ ] Email/Slack notifications
- [ ] Daemon mode with scheduling
- [ ] Certificate comparison tool
- [ ] CAA record checking
- [ ] DANE/TLSA validation

---

**Need help?** Open an issue on GitHub or check the documentation.
