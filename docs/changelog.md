# Changelog

All notable changes to cert-checker will be documented in this file.

## [0.1.0] - 2026-02-16

### Added
- Initial release
- Remote certificate checking with expiration monitoring
- Truststore management (JKS, PKCS12, PEM)
- Keystore management
- Certificate validation and chain verification
- Format conversion (PEM, DER, PKCS12, JKS)
- CLI interface with Click (15+ commands)
- TUI interface with Textual
- JSON/CSV export for automation
- Configuration management with TOML
- Complete documentation and test suite

### Fixed
- SSLSocket.getpeercert() method call
- JKS library password handling (string vs bytes)

### Documentation
- Complete README (~600 lines)
- Quick start guide
- Testing guide (~800 lines)
- Test cases (~900 lines)
- MkDocs documentation site
- GitHub Pages deployment

## [Unreleased]

### Planned
- OCSP stapling support
- Certificate Transparency monitoring
- HTML/PDF report generation
- Email/Slack notifications
- Daemon mode with scheduling
- Web dashboard
- REST API

---

Format based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)
