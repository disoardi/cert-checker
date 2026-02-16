# Installation Guide

## Method 1: Poetry (Recommended for Development)

```bash
# Clone repository
git clone https://github.com/disoardi/cert-checker.git
cd cert-checker

# Install with Poetry
poetry install

# Activate virtual environment
poetry shell

# Verify installation
cert-checker --version
```

## Method 2: pip

```bash
# Clone repository
git clone https://github.com/disoardi/cert-checker.git
cd cert-checker

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install
pip install -e .

# Verify installation
cert-checker --version
```

## Method 3: Docker

```bash
# Clone repository
git clone https://github.com/disoardi/cert-checker.git
cd cert-checker

# Build image
docker-compose build

# Run
docker-compose up
```

## Method 4: Standalone Binary (Coming Soon)

```bash
# Download from releases
wget https://github.com/disoardi/cert-checker/releases/latest/download/cert-checker

# Make executable
chmod +x cert-checker

# Run
./cert-checker --version
```

## Verify Installation

```bash
# Check version
cert-checker --version

# Run help
cert-checker --help

# Quick test
cert-checker check --host google.com --port 443
```

## Requirements

### System Requirements
- Python 3.8 or higher
- Java JRE (for JKS keystore operations)

### Python Dependencies
All dependencies are automatically installed:

- `cryptography>=41.0.0` - Certificate operations
- `pyOpenSSL>=23.0.0` - SSL/TLS operations
- `click>=8.1.0` - CLI framework
- `textual>=0.47.0` - TUI framework
- `rich>=13.7.0` - Beautiful output
- `pydantic>=2.5.0` - Configuration validation
- `pyjks>=20.0.0` - JKS keystore parser
- `toml>=0.10.2` - TOML configuration

### Installing Java (for JKS support)

=== "Ubuntu/Debian"
    ```bash
    sudo apt-get update
    sudo apt-get install default-jre
    keytool -version
    ```

=== "macOS"
    ```bash
    brew install openjdk
    keytool -version
    ```

=== "Red Hat/CentOS"
    ```bash
    sudo yum install java-11-openjdk
    keytool -version
    ```

## Troubleshooting

### Poetry Installation Issues

If you encounter the "Unknown metadata version: 2.4" warning:

```bash
# Option 1: Ignore it (installation will complete)
poetry install

# Option 2: Upgrade Poetry
poetry self update

# Option 3: Use pip instead
pip install -e .
```

### Permission Errors

```bash
# Ensure you have write permissions
chmod 755 ~/.local/bin

# Or use user install
pip install --user -e .
```

### Import Errors

```bash
# Ensure virtual environment is activated
poetry shell
# or
source .venv/bin/activate

# Verify installation
pip list | grep cert-checker
```

## Next Steps

- [Quick Start Guide](quickstart.md)
- [Configuration Guide](configuration.md)
- [CLI Reference](cli-reference.md)
