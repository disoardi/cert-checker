# CLI Commands Reference

## Global Options

```bash
cert-checker --help              # Show help
cert-checker --version           # Show version
```

## check - Check Certificates

Check SSL/TLS certificates on remote hosts.

```bash
cert-checker check [OPTIONS]
```

### Options

| Option | Short | Type | Description |
|--------|-------|------|-------------|
| `--config` | `-c` | PATH | Configuration file |
| `--host` | `-h` | TEXT | Host FQDN |
| `--port` | `-p` | INTEGER | Port (default: 443) |
| `--timeout` | `-t` | INTEGER | Timeout in seconds (default: 10) |
| `--warning-days` | `-w` | INTEGER | Warning threshold days (default: 30) |
| `--verbose` | `-v` | FLAG | Verbose output |
| `--json` | | FLAG | JSON output format |
| `--csv` | | FLAG | CSV output format |

### Examples

```bash
# Single host
cert-checker check --host google.com --port 443

# With verbose output
cert-checker check --host api.example.com --verbose

# From configuration file
cert-checker check --config config.toml

# Export to JSON
cert-checker check --config config.toml --json > results.json

# Export to CSV
cert-checker check --config config.toml --csv > results.csv
```

## truststore - Manage Truststore

Manage trusted certificates in various formats.

### list - List Certificates

```bash
cert-checker truststore list --store PATH [OPTIONS]
```

**Options:**
- `--store`, `-s`: Truststore file path (required)
- `--password`, `-p`: Truststore password
- `--format`, `-f`: Format (jks, pkcs12, pem) - default: jks

**Example:**
```bash
cert-checker truststore list --store truststore.jks --password changeit
```

### add - Add Certificate

```bash
cert-checker truststore add --store PATH --cert PATH --alias TEXT [OPTIONS]
```

**Options:**
- `--store`, `-s`: Truststore file path (required)
- `--cert`, `-c`: Certificate file to add (required)
- `--alias`, `-a`: Certificate alias (required)
- `--password`, `-p`: Truststore password
- `--store-format`, `-f`: Truststore format (jks, pkcs12, pem)

**Example:**
```bash
cert-checker truststore add \
  --store truststore.jks \
  --cert ca-cert.pem \
  --alias my-ca \
  --password changeit
```

### export - Export Certificate

```bash
cert-checker truststore export --store PATH --alias TEXT --output PATH [OPTIONS]
```

**Options:**
- `--store`, `-s`: Truststore file path (required)
- `--alias`, `-a`: Certificate alias (required)
- `--output`, `-o`: Output file path (required)
- `--password`, `-p`: Truststore password
- `--store-format`: Input format (jks, pkcs12, pem)
- `--output-format`: Output format (pem, der)

**Example:**
```bash
cert-checker truststore export \
  --store truststore.jks \
  --alias my-ca \
  --output exported-cert.pem \
  --password changeit
```

### remove - Remove Certificate

```bash
cert-checker truststore remove --store PATH --alias TEXT [OPTIONS]
```

**Options:**
- `--store`, `-s`: Truststore file path (required)
- `--alias`, `-a`: Certificate alias (required)
- `--password`, `-p`: Truststore password
- `--format`, `-f`: Truststore format

**Example:**
```bash
cert-checker truststore remove \
  --store truststore.jks \
  --alias my-ca \
  --password changeit
```

## keystore - Manage Keystore

Manage private keys and certificates.

### list - List Entries

```bash
cert-checker keystore list --store PATH [OPTIONS]
```

**Options:**
- `--store`, `-s`: Keystore file path (required)
- `--password`, `-p`: Keystore password
- `--format`, `-f`: Format (jks, pkcs12) - default: pkcs12

**Example:**
```bash
cert-checker keystore list --store keystore.p12 --password changeit
```

### export - Export Entry

```bash
cert-checker keystore export --store PATH --alias TEXT --output PATH [OPTIONS]
```

**Options:**
- `--store`, `-s`: Keystore file path (required)
- `--alias`, `-a`: Entry alias (required)
- `--output`, `-o`: Output file path (required)
- `--password`, `-p`: Keystore password
- `--export-password`: Password for exported file
- `--format`: Input format (jks, pkcs12)
- `--output-format`: Output format (pkcs12, pem)

**Example:**
```bash
cert-checker keystore export \
  --store keystore.p12 \
  --alias my-key \
  --output exported.p12 \
  --password changeit \
  --export-password newpassword
```

## convert - Convert Certificates

Convert certificates between formats.

```bash
cert-checker convert --input PATH --output PATH --from FORMAT --to FORMAT [OPTIONS]
```

**Options:**
- `--input`, `-i`: Input file path (required)
- `--output`, `-o`: Output file path (required)
- `--from`: Input format (required): pem, der, pkcs12, jks
- `--to`: Output format (required): pem, der, pkcs12, jks
- `--password`, `-p`: Password (for JKS/PKCS12)

**Examples:**

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

## validate - Validate Certificates

Validate certificate and chain.

```bash
cert-checker validate --cert PATH [OPTIONS]
```

**Options:**
- `--cert`, `-c`: Certificate file (required)
- `--chain`: Chain certificate (can be used multiple times)
- `--truststore`, `-t`: Truststore for validation
- `--truststore-password`: Truststore password
- `--verbose`, `-v`: Verbose output

**Examples:**

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

## tui - Interactive TUI

Launch interactive text-based user interface.

```bash
cert-checker tui [--config PATH]
```

**Keyboard Shortcuts:**
- `r` - Refresh
- `q` - Quit
- `d` - Toggle dark mode
- `↑/↓` - Navigate
- `Enter` - View details

**Example:**
```bash
cert-checker tui --config config.toml
```

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | General error |
| 2 | Invalid arguments |
| 3 | File not found |
| 4 | Permission denied |

## Environment Variables

| Variable | Description |
|----------|-------------|
| `TRUSTSTORE_PASSWORD` | Default truststore password |
| `KEYSTORE_PASSWORD` | Default keystore password |
| `CERT_CHECKER_CONFIG` | Default config file path |

Use in configuration:
```toml
truststore_password = "${TRUSTSTORE_PASSWORD}"
```
