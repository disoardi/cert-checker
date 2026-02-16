# Test Cases - Validazione Funzionalità

## Test Case Summary

| ID | Categoria | Funzionalità | Priorità | Automatable |
|----|-----------|--------------|----------|-------------|
| TC01 | Remote Check | Check singolo host | Alta | ✅ |
| TC02 | Remote Check | Check multiplo da config | Alta | ✅ |
| TC03 | Remote Check | Export JSON/CSV | Media | ✅ |
| TC04 | Truststore | List certificates | Alta | ✅ |
| TC05 | Truststore | Add certificate | Alta | ✅ |
| TC06 | Truststore | Export certificate | Media | ✅ |
| TC07 | Truststore | Remove certificate | Media | ✅ |
| TC08 | Keystore | List entries | Alta | ✅ |
| TC09 | Keystore | Export entry | Media | ✅ |
| TC10 | Convert | PEM ↔ DER | Media | ✅ |
| TC11 | Convert | JKS ↔ PKCS12 | Media | ✅ |
| TC12 | Validate | Single certificate | Media | ✅ |
| TC13 | Validate | Certificate chain | Alta | ✅ |
| TC14 | TUI | Launch and navigate | Media | ❌ Manual |
| TC15 | Error Handling | Graceful failures | Alta | ✅ |

---

## TC01: Remote Certificate Check - Single Host

### Obiettivo
Verificare che il tool possa controllare correttamente un certificato SSL/TLS su un host remoto.

### Precondizioni
- Tool installato e funzionante
- Connessione internet attiva

### Steps
```bash
cert-checker check --host google.com --port 443
```

### Expected Result
```
✓ google.com (google.com:443)
Subject: *.google.com
Issuer: GTS CA 1C3
Valid Until: [data futura]
Days Remaining: [numero > 0]
Hostname: ✓ Valid
```

### Validation Checklist
- [ ] Connessione riuscita senza timeout
- [ ] Certificato recuperato
- [ ] Subject CN corretto
- [ ] Issuer visualizzato
- [ ] Data scadenza presente e futura
- [ ] Giorni rimanenti calcolati correttamente
- [ ] Hostname validation = Valid
- [ ] Status indicator verde (✓)

---

## TC02: Remote Check - Multiple Hosts from Config

### Obiettivo
Verificare il controllo batch di più host da file di configurazione.

### Precondizioni
- File config.toml creato con almeno 3 host
- Host configurati con `enabled = true`

### Setup
```bash
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
name = "Disabled"
fqdn = "example.com"
port = 443
enabled = false
EOF
```

### Steps
```bash
cert-checker check --config test-config.toml
```

### Expected Result
```
Certificate Check Summary
┌─────────┬──────────────────┬──────────┬────────────┬───────────┐
│ Host    │ FQDN:Port        │ Status   │ Expiry     │ Days Left │
├─────────┼──────────────────┼──────────┼────────────┼───────────┤
│ Google  │ google.com:443   │ ✓ Valid  │ 2025-XX-XX │ XX        │
│ GitHub  │ github.com:443   │ ✓ Valid  │ 2025-XX-XX │ XX        │
└─────────┴──────────────────┴──────────┴────────────┴───────────┘
```

### Validation Checklist
- [ ] Solo host enabled vengono controllati
- [ ] Tabella summary visualizzata
- [ ] Tutti gli host hanno Status
- [ ] Colonne formattate correttamente
- [ ] Date nel formato YYYY-MM-DD
- [ ] Days Left sono numeri positivi
- [ ] Host disabilitati non appaiono

---

## TC03: Export Formats - JSON and CSV

### Obiettivo
Verificare export dei risultati in formati machine-readable.

### Steps - JSON
```bash
cert-checker check --host google.com --port 443 --json
```

### Expected Result - JSON
```json
[
  {
    "host_name": "google.com",
    "fqdn": "google.com",
    "port": 443,
    "status": "valid",
    "certificate": {
      "subject_cn": "*.google.com",
      "issuer_cn": "GTS CA 1C3",
      "not_before": "2025-XX-XXTXX:XX:XX+00:00",
      "not_after": "2025-XX-XXTXX:XX:XX+00:00",
      "days_remaining": XX,
      "is_expired": false,
      "fingerprint": "XX:XX:..."
    },
    "hostname_valid": true
  }
]
```

### Steps - CSV
```bash
cert-checker check --host google.com --port 443 --csv
```

### Expected Result - CSV
```
Host,FQDN,Port,Status,Subject,Issuer,Expiry,Days Remaining,Error
google.com,google.com,443,valid,*.google.com,GTS CA 1C3,2025-XX-XX,XX,
```

### Validation Checklist - JSON
- [ ] Output è valid JSON (`jq .` passa)
- [ ] Contiene tutti i campi richiesti
- [ ] Date in formato ISO 8601
- [ ] Fingerprint presente

### Validation Checklist - CSV
- [ ] Header presente
- [ ] Campi separati da virgola
- [ ] Nessun campo con virgole non escapate
- [ ] Importabile in Excel/LibreOffice

---

## TC04: Truststore - List Certificates

### Obiettivo
Verificare listing dei certificati in un truststore JKS.

### Setup
```bash
# Crea certificato test
openssl req -x509 -newkey rsa:2048 -nodes \
  -keyout test-key.pem -out test-cert.pem -days 365 \
  -subj "/CN=test.example.com/O=Test Org/C=IT"

# Crea truststore
keytool -import -noprompt -trustcacerts \
  -alias test-ca \
  -file test-cert.pem \
  -keystore test-truststore.jks \
  -storepass changeit
```

### Steps
```bash
cert-checker truststore list \
  --store test-truststore.jks \
  --password changeit \
  --format jks
```

### Expected Result
```
Truststore Certificates
┌──────────┬───────────────────┬───────────┬────────────┬──────┐
│ Alias    │ Subject CN        │ Issuer CN │ Valid Until│ Type │
├──────────┼───────────────────┼───────────┼────────────┼──────┤
│ test-ca  │ test.example.com  │ test...   │ 2026-XX-XX │ Cert │
└──────────┴───────────────────┴───────────┴────────────┴──────┘
```

### Validation Checklist
- [ ] Certificato listato con alias corretto
- [ ] Subject CN visibile
- [ ] Issuer CN visibile
- [ ] Valid Until in formato leggibile
- [ ] Type indicato (Cert o CA)
- [ ] Nessun errore di password
- [ ] Tabella formattata correttamente

---

## TC05: Truststore - Add Certificate

### Obiettivo
Aggiungere un nuovo certificato a truststore esistente.

### Preconditions
- Truststore esistente da TC04
- Nuovo certificato da aggiungere

### Setup
```bash
# Crea secondo certificato
openssl req -x509 -newkey rsa:2048 -nodes \
  -keyout another-key.pem -out another-cert.pem -days 365 \
  -subj "/CN=another.example.com/O=Test/C=IT"
```

### Steps
```bash
cert-checker truststore add \
  --store test-truststore.jks \
  --cert another-cert.pem \
  --alias another-ca \
  --password changeit \
  --format jks
```

### Expected Result
```
✓ Certificate added successfully with alias: another-ca
```

### Validation
```bash
# Verifica con list
cert-checker truststore list \
  --store test-truststore.jks \
  --password changeit

# Expected: 2 certificati (test-ca e another-ca)
```

### Validation Checklist
- [ ] Messaggio di successo
- [ ] Nuovo certificato appare nel list
- [ ] Alias corretto
- [ ] Truststore non corrotto
- [ ] Certificato esistente ancora presente

---

## TC06: Truststore - Export Certificate

### Obiettivo
Esportare un certificato dal truststore in formato PEM.

### Preconditions
- Truststore con almeno un certificato

### Steps
```bash
cert-checker truststore export \
  --store test-truststore.jks \
  --alias test-ca \
  --output exported-cert.pem \
  --password changeit \
  --output-format pem
```

### Expected Result
```
✓ Certificate exported to exported-cert.pem
```

### Validation
```bash
# Verifica file creato
ls -la exported-cert.pem

# Verifica contenuto con openssl
openssl x509 -in exported-cert.pem -text -noout

# Expected: Certificate details printed
```

### Validation Checklist
- [ ] File creato
- [ ] File non vuoto
- [ ] Formato PEM valido (BEGIN CERTIFICATE)
- [ ] openssl può leggere il certificato
- [ ] Subject CN corretto

---

## TC07: Truststore - Remove Certificate

### Obiettivo
Rimuovere certificato da truststore.

### Preconditions
- Truststore con certificati da TC05

### Steps
```bash
cert-checker truststore remove \
  --store test-truststore.jks \
  --alias another-ca \
  --password changeit
```

### Expected Result
```
✓ Certificate 'another-ca' removed successfully
```

### Validation
```bash
cert-checker truststore list \
  --store test-truststore.jks \
  --password changeit

# Expected: Solo test-ca, another-ca non presente
```

### Validation Checklist
- [ ] Messaggio di successo
- [ ] Certificato non più nel list
- [ ] Altri certificati ancora presenti
- [ ] Truststore ancora funzionante

---

## TC08: Keystore - List Entries

### Obiettivo
Listare entries in keystore PKCS12.

### Setup
```bash
# Crea keystore PKCS12
openssl pkcs12 -export \
  -in test-cert.pem \
  -inkey test-key.pem \
  -out test-keystore.p12 \
  -name test-key \
  -passout pass:changeit
```

### Steps
```bash
cert-checker keystore list \
  --store test-keystore.p12 \
  --password changeit \
  --format pkcs12
```

### Expected Result
```
Keystore Entries
┌──────────┬──────────────────┬────────────┬─────────────┬─────────┐
│ Alias    │ Subject CN       │ Valid Until│ Chain Length│ Has Key │
├──────────┼──────────────────┼────────────┼─────────────┼─────────┤
│ test-key │ test.example.com │ 2026-XX-XX │ 1           │ ✓       │
└──────────┴──────────────────┴────────────┴─────────────┴─────────┘
```

### Validation Checklist
- [ ] Entry listato
- [ ] Alias corretto
- [ ] Subject CN visibile
- [ ] Chain Length > 0
- [ ] Has Key = ✓ (verde)
- [ ] Valid Until presente

---

## TC09: Keystore - Export Entry

### Obiettivo
Esportare entry (chiave + certificato) da keystore.

### Preconditions
- Keystore da TC08

### Steps
```bash
cert-checker keystore export \
  --store test-keystore.p12 \
  --alias test-key \
  --output exported-keystore.p12 \
  --password changeit \
  --export-password newpassword \
  --output-format pkcs12
```

### Expected Result
```
✓ Entry exported to exported-keystore.p12
```

### Validation
```bash
# Verifica con openssl
openssl pkcs12 -in exported-keystore.p12 \
  -passin pass:newpassword \
  -info

# Expected: Key and certificate info
```

### Validation Checklist
- [ ] File esportato
- [ ] Nuova password funziona
- [ ] Vecchia password non funziona sul file esportato
- [ ] Contiene chiave privata
- [ ] Contiene certificato

---

## TC10: Convert - PEM to DER and Back

### Obiettivo
Convertire certificato tra formati PEM e DER.

### Setup
Usa test-cert.pem da test precedenti

### Steps - PEM to DER
```bash
cert-checker convert \
  --input test-cert.pem \
  --output test-cert.der \
  --from pem \
  --to der
```

### Validation - DER Created
```bash
openssl x509 -in test-cert.der -inform der -text -noout
```

### Steps - DER to PEM
```bash
cert-checker convert \
  --input test-cert.der \
  --output test-cert-back.pem \
  --from der \
  --to pem
```

### Validation - Round Trip
```bash
# Compare fingerprints
openssl x509 -in test-cert.pem -fingerprint -noout
openssl x509 -in test-cert-back.pem -fingerprint -noout

# Should be identical
```

### Validation Checklist
- [ ] Conversione PEM→DER OK
- [ ] File DER creato
- [ ] openssl può leggere DER
- [ ] Conversione DER→PEM OK
- [ ] Fingerprint identici (round-trip successful)

---

## TC11: Convert - JKS to PKCS12

### Obiettivo
Convertire keystore da JKS a PKCS12.

### Preconditions
- keytool disponibile
- test-truststore.jks esistente

### Steps
```bash
cert-checker convert \
  --input test-truststore.jks \
  --output converted.p12 \
  --from jks \
  --to pkcs12 \
  --password changeit
```

### Expected Result
```
✓ Converted JKS to PKCS12: converted.p12
```

### Validation
```bash
openssl pkcs12 -in converted.p12 -passin pass:changeit -info
```

### Validation Checklist
- [ ] Conversione riuscita
- [ ] File PKCS12 creato
- [ ] openssl può leggere il file
- [ ] Certificati presenti
- [ ] Stesso numero di certificati

---

## TC12: Validate - Self-Signed Certificate

### Obiettivo
Validare certificato self-signed.

### Preconditions
- test-cert.pem esistente (self-signed)

### Steps
```bash
cert-checker validate --cert test-cert.pem --verbose
```

### Expected Result
```
✓ Certificate chain is valid

Validation Details:
  • Cert 0: Certificate is not a CA certificate
  • Cert 0: Key usage valid
  • Self-signed certificate with valid signature
```

### Validation Checklist
- [ ] Validazione completata
- [ ] Self-signed rilevato
- [ ] Signature valida
- [ ] Nessun crash

---

## TC13: Validate - Real Certificate Chain

### Obiettivo
Validare certificato con chain completa.

### Setup
```bash
# Download real certificate
echo | openssl s_client -showcerts -connect google.com:443 2>/dev/null | \
  openssl x509 -outform PEM > google-cert.pem
```

### Steps
```bash
cert-checker validate --cert google-cert.pem --verbose
```

### Expected Result
```
✓ Certificate chain is valid

Certificate Details
├─ Subject: *.google.com
├─ Issuer: GTS CA 1C3
├─ Validity
│  ├─ Not Before: ...
│  └─ Not After: ...
...
```

### Validation Checklist
- [ ] Certificato valido
- [ ] Dettagli visualizzati
- [ ] Nessun errore

---

## TC14: TUI - Interactive Interface (Manual)

### Obiettivo
Verificare funzionamento TUI interattivo.

### Preconditions
- Config file con hosts

### Steps
```bash
cert-checker tui --config test-config.toml
```

### Manual Test Steps
1. Verifica apertura TUI
2. Premi `r` per refresh
3. Usa `↑/↓` per navigare tra hosts
4. Premi `Enter` su un host
5. Verifica dettagli mostrati
6. Vai al tab "Details"
7. Premi `d` per toggle dark mode
8. Premi `q` per uscire

### Validation Checklist (Manual)
- [ ] TUI si apre senza errori
- [ ] Tab "Remote Hosts" visibile
- [ ] Tabella hosts popolata
- [ ] Refresh funziona (`r`)
- [ ] Navigazione frecce funziona
- [ ] Tab Details funziona
- [ ] Dettagli certificato mostrati
- [ ] Dark mode toggle funziona (`d`)
- [ ] Quit funziona (`q`)
- [ ] Colori corretti (verde/giallo/rosso)

---

## TC15: Error Handling

### Obiettivo
Verificare gestione errori graceful.

### Test Cases

#### TC15.1: Invalid Config TOML
```bash
echo "invalid [[[" > invalid.toml
cert-checker check --config invalid.toml
```
**Expected:** Clear error message, no crash

#### TC15.2: Non-existent Host
```bash
cert-checker check --host non-existent-123456.com --port 443
```
**Expected:** DNS error, status ERROR

#### TC15.3: Connection Timeout
```bash
cert-checker check --host 1.2.3.4 --port 443 --timeout 2
```
**Expected:** Timeout error after ~2s

#### TC15.4: Wrong Password
```bash
cert-checker truststore list \
  --store test-truststore.jks \
  --password wrongpassword
```
**Expected:** Password error, no crash

#### TC15.5: Missing File
```bash
cert-checker validate --cert non-existent.pem
```
**Expected:** File not found error

### Validation Checklist - Error Handling
- [ ] Nessun crash/exception non gestita
- [ ] Messaggi di errore chiari
- [ ] Exit code appropriato (non 0)
- [ ] Stack trace non mostrato all'utente
- [ ] Suggerimenti per correzione (quando possibile)

---

## Test Execution Summary

### Quick Automated Test
```bash
./scripts/quick-test.sh
```

### Full Manual Test Suite
```bash
# Follow TESTING.md step by step
```

### Docker Tests
```bash
# Build and test in Docker
docker-compose build
docker-compose up

# Test specific command
docker run --rm cert-checker check --host google.com --port 443
```

### Clean Up
```bash
rm -rf test-certs/
rm -f test-config.toml test-truststore.jks test-keystore.p12
rm -f exported-* converted.* google-cert.pem
```

---

## Success Criteria

Il tool è considerato funzionante se:

✅ **Core Functionality (Must Have)**
- TC01: Remote check singolo funziona
- TC02: Remote check multiplo da config funziona
- TC04: Truststore list funziona
- TC05: Truststore add funziona
- TC08: Keystore list funziona
- TC13: Validate funziona

✅ **Extended Functionality (Should Have)**
- TC03: Export JSON/CSV funziona
- TC06: Truststore export funziona
- TC09: Keystore export funziona
- TC10-11: Conversioni funzionano

✅ **User Experience (Nice to Have)**
- TC14: TUI funziona
- TC15: Error handling graceful
- Output colorato e leggibile
- Performance accettabile

✅ **Quality (Essential)**
- Nessun crash su input valido
- Errori gestiti gracefully
- Documentazione completa
- Docker funzionante
