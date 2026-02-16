# Testing Guide for cert-checker

Questa guida fornisce test case completi per validare tutte le funzionalità del cert-checker.

## Prerequisiti

```bash
# Setup ambiente
cd cert-checker
poetry install

# Attiva l'ambiente virtuale
poetry shell
```

## Test Case 1: Remote Certificate Checking

### TC1.1: Check Single Host (Google)
```bash
# Test base
cert-checker check --host google.com --port 443

# Expected Output:
# ✓ google.com (google.com:443)
# Subject: CN=*.google.com
# Issuer: CN=GTS CA 1C3
# Valid Until: [data futura]
# Days Remaining: [numero positivo]
# Hostname: ✓ Valid
```

**Validation:**
- ✅ Connessione riuscita
- ✅ Certificato recuperato
- ✅ Informazioni visualizzate correttamente
- ✅ Status: VALID (verde)

### TC1.2: Check con Output Verbose
```bash
cert-checker check --host github.com --port 443 --verbose

# Expected: Informazioni aggiuntive includono:
# - SAN (Subject Alternative Names)
# - Fingerprint SHA-256
# - Public key info
```

**Validation:**
- ✅ SAN mostrati
- ✅ Fingerprint visualizzato
- ✅ Maggiori dettagli presenti

### TC1.3: Check con Timeout Personalizzato
```bash
# Host lento o irraggiungibile
cert-checker check --host 1.2.3.4 --port 443 --timeout 5

# Expected Output:
# ✗ Error
# Connection timeout after 5s
```

**Validation:**
- ✅ Timeout rispettato
- ✅ Errore gestito correttamente

### TC1.4: Check Invalid Hostname
```bash
cert-checker check --host expired.badssl.com --port 443

# Expected Output:
# ✗ Expired o Warning
# Status: EXPIRED (rosso)
```

**Validation:**
- ✅ Certificato scaduto rilevato
- ✅ Status corretto

### TC1.5: Export JSON
```bash
cert-checker check --host google.com --port 443 --json

# Expected: Valid JSON output
```

**Validation:**
```bash
# Verifica che sia JSON valido
cert-checker check --host google.com --port 443 --json | jq .
```

### TC1.6: Export CSV
```bash
cert-checker check --host google.com --port 443 --csv

# Expected: CSV with headers
# Host,FQDN,Port,Status,Subject,Issuer,Expiry,Days Remaining,Error
```

**Validation:**
- ✅ Header presente
- ✅ Dati formattati correttamente

## Test Case 2: Configuration File

### TC2.1: Create and Use Config File
```bash
# Crea config personalizzato
cat > test-config.toml << EOF
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

[[hosts]]
name = "Disabled Host"
fqdn = "example.com"
port = 443
enabled = false
EOF

# Run check
cert-checker check --config test-config.toml

# Expected: Summary table con Google e GitHub (non example.com)
```

**Validation:**
- ✅ Solo host enabled vengono controllati
- ✅ Tabella summary visualizzata
- ✅ Status colorati correttamente

### TC2.2: Config con Environment Variables
```bash
# Set environment variable
export TEST_PASSWORD="my-secret-password"

# Create config
cat > test-env-config.toml << EOF
[settings]
timeout = 10

[stores]
truststore_password = "\${TEST_PASSWORD}"

[[hosts]]
name = "Test Host"
fqdn = "google.com"
port = 443
enabled = true
EOF

# Verify password expansion (will need truststore to fully test)
```

**Validation:**
- ✅ Environment variable espansa correttamente

## Test Case 3: Certificate Generation per Testing

### TC3.1: Generate Self-Signed Certificate
```bash
# Create test directory
mkdir -p test-certs
cd test-certs

# Generate self-signed certificate
openssl req -x509 -newkey rsa:2048 -nodes \
  -keyout test-key.pem \
  -out test-cert.pem \
  -days 365 \
  -subj "/CN=test.example.com/O=Test Org/C=IT"

# Generate expired certificate (backdated)
openssl req -x509 -newkey rsa:2048 -nodes \
  -keyout expired-key.pem \
  -out expired-cert.pem \
  -days 1 \
  -subj "/CN=expired.example.com/O=Test Org/C=IT"

# Set date back
touch -t 202001010000 expired-cert.pem

cd ..
```

### TC3.2: Create Test Truststore (JKS)
```bash
# Import certificate into JKS truststore
keytool -import -noprompt -trustcacerts \
  -alias test-ca \
  -file test-certs/test-cert.pem \
  -keystore test-certs/test-truststore.jks \
  -storepass changeit

# Verify
keytool -list -keystore test-certs/test-truststore.jks -storepass changeit
```

### TC3.3: Create Test Keystore (PKCS12)
```bash
# Convert to PKCS12
openssl pkcs12 -export \
  -in test-certs/test-cert.pem \
  -inkey test-certs/test-key.pem \
  -out test-certs/test-keystore.p12 \
  -name test-key \
  -passout pass:changeit
```

## Test Case 4: Truststore Management

### TC4.1: List Truststore
```bash
cert-checker truststore list \
  --store test-certs/test-truststore.jks \
  --password changeit \
  --format jks

# Expected: Table with certificate details
```

**Validation:**
- ✅ Certificato listato con alias
- ✅ Subject CN visualizzato
- ✅ Issuer CN visualizzato
- ✅ Data scadenza presente

### TC4.2: Add Certificate to Truststore
```bash
# Generate another cert
openssl req -x509 -newkey rsa:2048 -nodes \
  -keyout test-certs/another-key.pem \
  -out test-certs/another-cert.pem \
  -days 365 \
  -subj "/CN=another.example.com/O=Test/C=IT"

# Add to truststore
cert-checker truststore add \
  --store test-certs/test-truststore.jks \
  --cert test-certs/another-cert.pem \
  --alias another-ca \
  --password changeit \
  --format jks

# Verify
cert-checker truststore list \
  --store test-certs/test-truststore.jks \
  --password changeit
```

**Validation:**
- ✅ Certificato aggiunto con successo
- ✅ Nuovo certificato appare nel list

### TC4.3: Export Certificate from Truststore
```bash
cert-checker truststore export \
  --store test-certs/test-truststore.jks \
  --alias test-ca \
  --output test-certs/exported-cert.pem \
  --password changeit \
  --output-format pem

# Verify exported certificate
openssl x509 -in test-certs/exported-cert.pem -text -noout
```

**Validation:**
- ✅ Certificato esportato
- ✅ File PEM valido
- ✅ Contenuto corretto

### TC4.4: Remove Certificate from Truststore
```bash
cert-checker truststore remove \
  --store test-certs/test-truststore.jks \
  --alias another-ca \
  --password changeit

# Verify removal
cert-checker truststore list \
  --store test-certs/test-truststore.jks \
  --password changeit
```

**Validation:**
- ✅ Certificato rimosso
- ✅ Non appare più nel list

## Test Case 5: Keystore Management

### TC5.1: List Keystore
```bash
cert-checker keystore list \
  --store test-certs/test-keystore.p12 \
  --password changeit \
  --format pkcs12

# Expected: Table with key entries
```

**Validation:**
- ✅ Entry listato
- ✅ Chain length mostrato
- ✅ Has Key: ✓

### TC5.2: Export Keystore Entry
```bash
cert-checker keystore export \
  --store test-certs/test-keystore.p12 \
  --alias test-key \
  --output test-certs/exported-keystore.p12 \
  --password changeit \
  --export-password newpassword \
  --output-format pkcs12

# Verify with openssl
openssl pkcs12 -in test-certs/exported-keystore.p12 -passin pass:newpassword -info
```

**Validation:**
- ✅ Export riuscito
- ✅ Password cambiata
- ✅ Contenuto valido

## Test Case 6: Format Conversion

### TC6.1: PEM to DER
```bash
cert-checker convert \
  --input test-certs/test-cert.pem \
  --output test-certs/test-cert.der \
  --from pem \
  --to der

# Verify
openssl x509 -in test-certs/test-cert.der -inform der -text -noout
```

**Validation:**
- ✅ Conversione riuscita
- ✅ File DER valido

### TC6.2: DER to PEM
```bash
cert-checker convert \
  --input test-certs/test-cert.der \
  --output test-certs/test-cert-reconverted.pem \
  --from der \
  --to pem

# Compare with original
diff test-certs/test-cert.pem test-certs/test-cert-reconverted.pem
```

**Validation:**
- ✅ Conversione riuscita
- ✅ File identico all'originale

### TC6.3: JKS to PKCS12
```bash
cert-checker convert \
  --input test-certs/test-truststore.jks \
  --output test-certs/converted.p12 \
  --from jks \
  --to pkcs12 \
  --password changeit

# Verify
openssl pkcs12 -in test-certs/converted.p12 -passin pass:changeit -info
```

**Validation:**
- ✅ Conversione riuscita
- ✅ PKCS12 valido

## Test Case 7: Certificate Validation

### TC7.1: Validate Single Certificate
```bash
cert-checker validate \
  --cert test-certs/test-cert.pem \
  --verbose

# Expected: Self-signed certificate validation info
```

**Validation:**
- ✅ Validazione completata
- ✅ Self-signed rilevato

### TC7.2: Validate Real Certificate Chain
```bash
# Download real certificate
echo | openssl s_client -showcerts -connect google.com:443 2>/dev/null | \
  openssl x509 -outform PEM > test-certs/google-cert.pem

cert-checker validate \
  --cert test-certs/google-cert.pem \
  --verbose
```

**Validation:**
- ✅ Certificato valido
- ✅ Chain info mostrate

## Test Case 8: TUI (Interactive)

### TC8.1: Launch TUI
```bash
cert-checker tui --config test-config.toml
```

**Manual Testing:**
- ✅ TUI si apre correttamente
- ✅ Tab "Remote Hosts" visibile
- ✅ Premere 'r' per refresh
- ✅ Navigazione con frecce funziona
- ✅ Tab "Details" mostra info selezionate
- ✅ Premere 'd' per toggle dark mode
- ✅ Premere 'q' per uscire

## Test Case 9: Docker

### TC9.1: Build Docker Image
```bash
docker-compose build

# Expected: Successful build
```

**Validation:**
- ✅ Build completato senza errori
- ✅ Immagine creata

### TC9.2: Run in Docker
```bash
# Create config for docker
cp test-config.toml config/config.toml

# Run
docker-compose up

# Expected: Check results printed
```

**Validation:**
- ✅ Container avviato
- ✅ Check eseguiti
- ✅ Output corretto

### TC9.3: Run Specific Command in Docker
```bash
docker run --rm \
  -v $(pwd)/test-certs:/certs \
  cert-checker \
  truststore list --store /certs/test-truststore.jks --password changeit
```

**Validation:**
- ✅ Comando eseguito in container
- ✅ Volume montato correttamente

## Test Case 10: Error Handling

### TC10.1: Invalid Config File
```bash
# Create invalid TOML
echo "invalid toml [[[" > invalid-config.toml

cert-checker check --config invalid-config.toml

# Expected: Clear error message
```

**Validation:**
- ✅ Errore gestito gracefully
- ✅ Messaggio chiaro

### TC10.2: Non-Existent Host
```bash
cert-checker check --host non-existent-host-12345.com --port 443

# Expected: DNS resolution error
```

**Validation:**
- ✅ Errore DNS caught
- ✅ Status: ERROR

### TC10.3: Wrong Password
```bash
cert-checker truststore list \
  --store test-certs/test-truststore.jks \
  --password wrongpassword

# Expected: Password error
```

**Validation:**
- ✅ Errore password chiaro
- ✅ Nessun crash

### TC10.4: Missing File
```bash
cert-checker validate --cert non-existent-file.pem

# Expected: File not found error
```

**Validation:**
- ✅ Errore file not found
- ✅ Messaggio chiaro

## Test Case 11: Performance

### TC11.1: Multiple Hosts Check
```bash
# Create config with many hosts
cat > perf-test-config.toml << EOF
[settings]
timeout = 10

[[hosts]]
name = "Host 1"
fqdn = "google.com"
port = 443
enabled = true

[[hosts]]
name = "Host 2"
fqdn = "github.com"
port = 443
enabled = true

[[hosts]]
name = "Host 3"
fqdn = "gitlab.com"
port = 443
enabled = true

[[hosts]]
name = "Host 4"
fqdn = "bitbucket.org"
port = 443
enabled = true

[[hosts]]
name = "Host 5"
fqdn = "stackoverflow.com"
port = 443
enabled = true
EOF

# Time the execution
time cert-checker check --config perf-test-config.toml
```

**Validation:**
- ✅ Tutti gli host controllati
- ✅ Tempo ragionevole (< 60s per 5 hosts)

## Automated Test Suite

### TC12.1: Run Unit Tests (when implemented)
```bash
# Run pytest
poetry run pytest tests/ -v

# With coverage
poetry run pytest tests/ -v --cov=cert_checker --cov-report=term-missing
```

## Clean Up

```bash
# Remove test files
rm -rf test-certs/
rm -f test-config.toml invalid-config.toml perf-test-config.toml test-env-config.toml

# Or use Make
make clean
```

## Summary Checklist

Esegui tutti i test e verifica:

- [ ] TC1: Remote certificate checking
- [ ] TC2: Configuration file handling
- [ ] TC3: Certificate generation
- [ ] TC4: Truststore management
- [ ] TC5: Keystore management
- [ ] TC6: Format conversion
- [ ] TC7: Certificate validation
- [ ] TC8: TUI functionality
- [ ] TC9: Docker execution
- [ ] TC10: Error handling
- [ ] TC11: Performance

## Risultati Attesi

Tutti i test dovrebbero:
- ✅ Eseguire senza crash
- ✅ Mostrare output formattato correttamente
- ✅ Gestire errori gracefully
- ✅ Rispettare i timeout
- ✅ Preservare i dati durante conversioni

## Report Issues

Se trovi problemi durante i test:
1. Annota il comando esatto
2. Copia l'output completo
3. Verifica la versione: `cert-checker --version`
4. Controlla i log se disponibili
5. Apri una issue su GitHub
