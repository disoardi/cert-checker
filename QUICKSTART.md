# Quick Start Guide

Guida rapida per iniziare ad usare cert-checker in 5 minuti.

## 1. Installazione (30 secondi)

```bash
cd cert-checker
poetry install
poetry shell
```

## 2. Primo Test - Controllo Certificato Remoto (10 secondi)

```bash
# Check immediato di un certificato
cert-checker check --host google.com --port 443
```

**Output atteso:**
```
┌─ ✓ google.com (google.com:443) ─────────────────────┐
│ Subject: *.google.com                                │
│ Issuer: GTS CA 1C3                                   │
│ Valid Until: 2025-05-15 12:34:56 UTC                 │
│ Days Remaining: 89 days                              │
│ Hostname: ✓ Valid                                    │
└──────────────────────────────────────────────────────┘
```

## 3. Controllo Multiplo con Config (2 minuti)

### Crea config.toml
```bash
cat > my-config.toml << 'EOF'
[settings]
timeout = 10
warning_days = 30

[[hosts]]
name = "Google"
fqdn = "google.com"
port = 443
enabled = true

[[hosts]]
name = "GitHub"
fqdn = "github.com"
port = 443
enabled = true
EOF
```

### Esegui check
```bash
cert-checker check --config my-config.toml
```

**Output atteso:**
```
Certificate Check Summary
┌─────────┬───────────────────┬────────────┬────────────┬───────────┐
│ Host    │ FQDN:Port         │ Status     │ Expiry     │ Days Left │
├─────────┼───────────────────┼────────────┼────────────┼───────────┤
│ Google  │ google.com:443    │ ✓ Valid    │ 2025-05-15 │ 89        │
│ GitHub  │ github.com:443    │ ✓ Valid    │ 2025-06-20 │ 125       │
└─────────┴───────────────────┴────────────┴────────────┴───────────┘
```

## 4. Gestione Truststore (2 minuti)

### Crea certificato test
```bash
openssl req -x509 -newkey rsa:2048 -nodes \
  -keyout test-key.pem -out test-cert.pem -days 365 \
  -subj "/CN=test.example.com/O=Test/C=IT"
```

### Crea truststore e aggiungi certificato
```bash
# Crea truststore JKS
keytool -import -noprompt -trustcacerts \
  -alias my-test-ca \
  -file test-cert.pem \
  -keystore my-truststore.jks \
  -storepass changeit

# Lista certificati
cert-checker truststore list \
  --store my-truststore.jks \
  --password changeit
```

## 5. TUI Interattivo (30 secondi)

```bash
cert-checker tui --config my-config.toml
```

**Controlli:**
- `r` - Refresh
- `↑/↓` - Navigazione
- `Tab` - Cambia tab
- `d` - Toggle dark mode
- `q` - Esci

## Comandi Più Usati

### Check Certificati
```bash
# Singolo host
cert-checker check --host example.com --port 443

# Da config con output JSON
cert-checker check --config config.toml --json

# Con dettagli verbose
cert-checker check --host example.com -v
```

### Truststore
```bash
# Lista
cert-checker truststore list --store truststore.jks --password changeit

# Aggiungi
cert-checker truststore add \
  --store truststore.jks \
  --cert new-cert.pem \
  --alias new-ca \
  --password changeit

# Esporta
cert-checker truststore export \
  --store truststore.jks \
  --alias my-ca \
  --output exported.pem \
  --password changeit
```

### Conversione Formati
```bash
# PEM → DER
cert-checker convert --input cert.pem --output cert.der --from pem --to der

# JKS → PKCS12
cert-checker convert \
  --input keystore.jks \
  --output keystore.p12 \
  --from jks \
  --to pkcs12 \
  --password changeit
```

### Validazione
```bash
# Valida certificato
cert-checker validate --cert server.crt --verbose

# Valida con chain
cert-checker validate \
  --cert server.crt \
  --chain intermediate.crt \
  --truststore truststore.jks
```

## Docker Quick Start

```bash
# Build
docker-compose build

# Run con config
docker-compose up

# Comando specifico
docker run --rm \
  -v $(pwd):/data \
  cert-checker \
  check --host google.com --port 443
```

## Test Completi

### Script automatico
```bash
./scripts/quick-test.sh
```

### Test manuali completi
Vedi `TESTING.md` per la suite completa di test.

## Troubleshooting Rapido

### Errore: "cert-checker: command not found"
```bash
# Attiva l'ambiente Poetry
poetry shell
```

### Errore: "keytool: command not found"
```bash
# Installa Java JRE
# Ubuntu/Debian
sudo apt-get install default-jre

# macOS
brew install openjdk
```

### Errore: "Permission denied" su keystore
```bash
# Verifica permessi
ls -la my-truststore.jks

# Correggi permessi
chmod 600 my-truststore.jks
```

### Certificato scaduto nei test
```bash
# Alcuni siti hanno certificati test scaduti di proposito
# Usa google.com o github.com per test affidabili
cert-checker check --host google.com --port 443
```

## Prossimi Passi

1. **Personalizza config**: Copia `config.toml.example` e personalizzalo
2. **Automatizza**: Crea cronjob per check periodici
3. **Integra**: Usa output JSON/CSV per monitoring
4. **Esplora**: Prova tutte le funzionalità in `cert-checker --help`

## Makefile Commands

```bash
make help              # Mostra comandi disponibili
make install           # Installa dipendenze
make test             # Run tests
make check-google     # Quick test su google.com
make tui              # Lancia TUI
make docker-build     # Build Docker image
```

## Links Utili

- **Full Documentation**: `README.md`
- **Complete Testing**: `TESTING.md`
- **Project Structure**: Vedi `README.md` sezione "Project Structure"
- **CLI Reference**: `cert-checker --help`

## Esempi Reali

### Scenario 1: Monitoraggio Server Aziendali
```toml
# production-config.toml
[settings]
warning_days = 15  # Alert 15 giorni prima

[[hosts]]
name = "Production API"
fqdn = "api.company.com"
port = 443
enabled = true

[[hosts]]
name = "Internal DB"
fqdn = "db.internal.company.com"
port = 5432
enabled = true
```

```bash
cert-checker check --config production-config.toml --json > daily-report.json
```

### Scenario 2: Gestione CA Interna
```bash
# Importa tutti i certificati CA
for cert in ca-certs/*.pem; do
    cert-checker truststore add \
        --store company-truststore.jks \
        --cert "$cert" \
        --alias "$(basename $cert .pem)" \
        --password "${CA_PASSWORD}"
done

# Verifica
cert-checker truststore list \
    --store company-truststore.jks \
    --password "${CA_PASSWORD}"
```

### Scenario 3: CI/CD Integration
```bash
#!/bin/bash
# check-certs.sh - In pipeline CI/CD

cert-checker check --config production-config.toml --json > results.json

# Check se ci sono certificati scaduti o in warning
if jq -e '.[] | select(.status == "expired" or .status == "warning")' results.json; then
    echo "⚠️  Certificati in scadenza rilevati!"
    exit 1
fi

echo "✓ Tutti i certificati sono validi"
```

## Done! 🎉

Ora sei pronto per usare cert-checker. Buon lavoro! 🔐
