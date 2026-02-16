# cert-checker 🔐

**Swiss Army knife for SSL/TLS certificate management and verification**

A comprehensive, portable tool for checking, managing, and validating SSL/TLS certificates. Perfect for DevOps, SysAdmins, and Security Engineers who need to monitor certificate expiration, manage truststores/keystores, and validate certificate chains.

## Features at a Glance

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

## Quick Start

```bash
# Install with Poetry
poetry install
poetry shell

# Quick test
cert-checker check --host google.com --port 443

# With configuration
cp config.toml.example config.toml
cert-checker check --config config.toml
```

## Example Output

```
╭───────────── ✓ google.com (google.com:443) ─────────────╮
│ Subject: *.google.com                                    │
│ Issuer: WR2                                              │
│ Valid Until: 2026-04-20 08:39:19 UTC                     │
│ Days Remaining: 62 days                                  │
│ Hostname: ✓ Valid                                        │
╰──────────────────────────────────────────────────────────╯
```

## Navigation

- **[Quick Start](quickstart.md)** - Get started in 5 minutes
- **[Installation](installation.md)** - Detailed installation guide
- **[CLI Reference](cli-reference.md)** - Complete command reference
- **[Testing Guide](testing.md)** - Test procedures and validation

## Requirements

- Python 3.8+
- Java JRE (for JKS operations with keytool)
- Dependencies (automatically installed):
  - cryptography, pyOpenSSL, click, rich, textual, pydantic, pyjks

## License

MIT License - see [License](license.md) for details.

## Contributing

Contributions are welcome! See [Contributing Guide](development/contributing.md).
