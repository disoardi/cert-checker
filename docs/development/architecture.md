# Architecture

## Overview

cert-checker follows a modular architecture with clear separation of concerns:

```
┌─────────────────────────────────────────────┐
│              CLI / TUI                      │
│         (User Interface Layer)              │
├─────────────────────────────────────────────┤
│     Checker      Store       Validator      │
│  (Business Logic Layer)                     │
├─────────────────────────────────────────────┤
│     Cert Parser      Display Utils          │
│        (Utility Layer)                      │
├─────────────────────────────────────────────┤
│  cryptography  pyOpenSSL  pyjks  Rich       │
│        (External Dependencies)              │
└─────────────────────────────────────────────┘
```

## Design Principles

1. **Modularity** - Each feature in separate module
2. **Type Safety** - Type hints throughout
3. **Error Handling** - Comprehensive exception handling
4. **User Experience** - Beautiful, informative output
5. **Testability** - Clear interfaces for testing

## Key Components

### CLI Layer
- Click-based command structure
- Input validation
- Output formatting (table, JSON, CSV)

### Business Logic
- **Checker**: Remote certificate fetching, validation
- **Store**: Truststore/keystore management
- **Converter**: Format conversion

### Utility Layer
- **Parser**: X.509 certificate parsing
- **Display**: Rich/Textual formatting

## Data Flow

```
User Input → CLI → Config → Business Logic → Utils → External Libs
                                     ↓
User Output ← Display ← Results ← Processing ← Certificate Data
```

## Error Handling Strategy

```python
try:
    result = risky_operation()
except SpecificError as e:
    console.print(f"[red]Error:[/red] {e}")
    raise click.Abort()
```

## Future Enhancements

- Plugin system for extensibility
- REST API layer
- Web dashboard
- Message queue integration
