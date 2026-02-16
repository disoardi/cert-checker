# Contributing Guide

Thank you for considering contributing to cert-checker!

## Getting Started

1. **Fork the repository**
   ```bash
   gh repo fork disoardi/cert-checker
   ```

2. **Clone your fork**
   ```bash
   git clone https://github.com/YOUR_USERNAME/cert-checker.git
   cd cert-checker
   ```

3. **Install development dependencies**
   ```bash
   poetry install
   poetry shell
   ```

4. **Create a branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

## Development Workflow

### Running Tests

```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=cert_checker

# Run quick test suite
bash scripts/quick-test.sh
```

### Code Quality

```bash
# Format code
poetry run black cert_checker/

# Lint code
poetry run flake8 cert_checker/

# Type checking
poetry run mypy cert_checker/
```

### Testing Changes

```bash
# Install in development mode
pip install -e .

# Test your changes
cert-checker --help
cert-checker check --host google.com --port 443
```

## Commit Messages

Follow conventional commits:

```
feat: add OCSP stapling support
fix: resolve SSL handshake timeout
docs: update installation guide
test: add keystore management tests
```

## Pull Request Process

1. **Update documentation** if needed
2. **Add tests** for new features
3. **Ensure all tests pass**
4. **Update CHANGELOG.md**
5. **Submit PR** with clear description

## Code Style

- Follow PEP 8
- Use type hints
- Add docstrings (Google style)
- Keep functions focused and small
- Use Rich for pretty output

## Questions?

Open an issue or discussion on GitHub!
