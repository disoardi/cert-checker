# Configuration Guide

## Configuration File Format

cert-checker uses TOML format for configuration, which is human-readable and easy to edit.

## Basic Configuration

Create a `config.toml` file:

```toml
[settings]
timeout = 10              # Connection timeout in seconds
warning_days = 30         # Warning threshold for certificate expiration
verify_chain = true       # Verify certificate chains
show_warnings = true      # Show warning messages
default_port = 443        # Default port for HTTPS
```

## Host Configuration

Add hosts to monitor:

```toml
[[hosts]]
name = "Production API"
fqdn = "api.example.com"
port = 443
enabled = true
warning_days = 30         # Override global warning_days for this host
client_cert = false
```

## Store Configuration

Configure truststore and keystore:

```toml
[stores]
truststore = "/path/to/truststore.jks"
truststore_password = "${TRUSTSTORE_PASSWORD}"  # Use environment variable
keystore = "/path/to/keystore.p12"
keystore_password = "${KEYSTORE_PASSWORD}"
```

## Environment Variables

Store sensitive data in environment variables:

```bash
# Set environment variables
export TRUSTSTORE_PASSWORD="my-secret-password"
export KEYSTORE_PASSWORD="another-secret"

# Reference in config.toml
truststore_password = "${TRUSTSTORE_PASSWORD}"
```

## Complete Example

```toml
# config.toml - Complete example

[settings]
timeout = 10
verify_chain = true
show_warnings = true
default_port = 443
warning_days = 30

[stores]
truststore = "/opt/certs/truststore.jks"
truststore_password = "${TRUSTSTORE_PASSWORD}"
keystore = "/opt/certs/keystore.p12"
keystore_password = "${KEYSTORE_PASSWORD}"

# Production hosts
[[hosts]]
name = "Production API"
fqdn = "api.example.com"
port = 443
enabled = true
warning_days = 15
client_cert = false

[[hosts]]
name = "Production Web"
fqdn = "www.example.com"
port = 443
enabled = true
warning_days = 30
client_cert = false

# Internal services
[[hosts]]
name = "Internal Database"
fqdn = "db.internal.example.com"
port = 5432
enabled = true
warning_days = 7
client_cert = true

[[hosts]]
name = "Internal LDAP"
fqdn = "ldap.internal.example.com"
port = 636
enabled = false  # Temporarily disabled
warning_days = 15
client_cert = true
```

## Usage

```bash
# Use configuration file
cert-checker check --config config.toml

# Export results
cert-checker check --config config.toml --json > results.json
cert-checker check --config config.toml --csv > results.csv

# Use with TUI
cert-checker tui --config config.toml
```

## Best Practices

1. **Never commit passwords** - Use environment variables
2. **Use specific warning thresholds** - Different hosts may need different warnings
3. **Disable temporarily** - Use `enabled = false` instead of deleting entries
4. **Document hosts** - Use descriptive names
5. **Organize by environment** - Create separate configs for dev/staging/prod

## Template

Copy the example configuration:

```bash
cp config.toml.example config.toml
vim config.toml
```

## Next Steps

- [CLI Reference](cli-reference.md)
- [Remote Checking Guide](guide/remote-checking.md)
- [Testing Guide](testing.md)
