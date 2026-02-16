# Project Structure

## Directory Layout

```
cert-checker/
├── cert_checker/              # Main package
│   ├── __init__.py
│   ├── __main__.py           # Entry point
│   ├── cli.py                # CLI interface (Click)
│   ├── tui.py                # TUI interface (Textual)
│   ├── config.py             # Configuration parser
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
├── docs/                     # MkDocs documentation
├── scripts/                  # Helper scripts
│   └── quick-test.sh         # Quick test automation
│
├── pyproject.toml            # Poetry configuration
├── mkdocs.yml                # MkDocs configuration
├── Dockerfile                # Docker build
├── docker-compose.yml        # Docker Compose
└── README.md                 # Main documentation
```

## Module Organization

### CLI (`cert_checker/cli.py`)
- Command-line interface using Click
- 15+ commands organized in groups
- Input validation and error handling

### TUI (`cert_checker/tui.py`)
- Interactive interface using Textual
- Real-time certificate monitoring
- Keyboard navigation

### Checker (`cert_checker/checker/`)
- `remote.py`: Remote certificate fetching via SSL/TLS
- `validator.py`: Certificate chain validation

### Store (`cert_checker/store/`)
- `truststore.py`: Truststore management (JKS, PKCS12, PEM)
- `keystore.py`: Keystore operations
- `converter.py`: Format conversion logic

### Utils (`cert_checker/utils/`)
- `cert_parser.py`: X.509 certificate parsing
- `display.py`: Rich/Textual output formatting

## Code Statistics

| Module | Files | LoC | Completeness |
|--------|-------|-----|--------------|
| CLI | 1 | ~450 | 100% ✅ |
| TUI | 1 | ~250 | 100% ✅ |
| Config | 1 | ~120 | 100% ✅ |
| Remote Checker | 1 | ~350 | 100% ✅ |
| Validator | 1 | ~300 | 100% ✅ |
| Truststore | 1 | ~380 | 100% ✅ |
| Keystore | 1 | ~350 | 100% ✅ |
| Converter | 1 | ~280 | 100% ✅ |
| Cert Parser | 1 | ~380 | 100% ✅ |
| Display | 1 | ~430 | 100% ✅ |
| **TOTAL** | **10** | **~3,290** | **100%** ✅ |
