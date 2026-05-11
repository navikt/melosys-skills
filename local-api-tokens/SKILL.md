---
name: local-api-tokens
description: Generate OAuth tokens and call local Melosys services (melosys-api, melosys-eessi, eux-rina-api, melosys-mock). Use when debugging API calls, testing endpoints, or needing authentication tokens for local development.
---

# Local API Token Generation

Generate and use OAuth tokens for calling local Melosys services.

## Quick Reference

| Service | Port | Token Variable | How to Generate |
|---------|------|----------------|-----------------|
| melosys-mock | 8083 | None needed | Direct access |
| melosys-api | 8080 | MELOSYS_TOKEN | `audience=melosys-localhost` |
| melosys-eessi | 8081 | MELOSYS_TOKEN | `audience=melosys-localhost` |
| eux-rina-api | 9090 | EUX_TOKEN | `scope=dummy` |

## Token Generation

**Important:** Tokens must be generated fresh via mock-oauth2-server. Pre-generated tokens will fail signature validation.

### MELOSYS_TOKEN (melosys-api, melosys-eessi)

```bash
export MELOSYS_TOKEN=$(curl -s -X POST "http://localhost:8082/isso/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=client_credentials&client_id=melosys-api&client_secret=dummy&audience=melosys-localhost" \
  | jq -r '.access_token')
```

### EUX_TOKEN (eux-rina-api)

```bash
export EUX_TOKEN=$(curl -s -X POST "http://localhost:8082/isso/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=client_credentials&client_id=melosys-eessi&client_secret=dummy&scope=dummy" \
  | jq -r '.access_token')
```

### Generate All Tokens (One-liner)

```bash
export MELOSYS_TOKEN=$(curl -s -X POST "http://localhost:8082/isso/token" -d "grant_type=client_credentials&client_id=melosys-api&client_secret=dummy&audience=melosys-localhost" | jq -r '.access_token') && \
export EUX_TOKEN=$(curl -s -X POST "http://localhost:8082/isso/token" -d "grant_type=client_credentials&client_id=melosys-eessi&client_secret=dummy&scope=dummy" | jq -r '.access_token') && \
echo "Tokens generated. Expires in ~2 minutes."
```

## Common API Calls

### melosys-mock (no auth)

```bash
# RINA CPI - Get case
curl -s "http://localhost:8083/eessiRest/Cases/{caseId}" | jq .

# EUX endpoint - Get BUC
curl -s "http://localhost:8083/eux/cpi/buc/{bucId}" | jq .

# Admin - List all cases in RinaCaseStore
curl -s "http://localhost:8083/rina/admin/cases" | jq .

# Verify saksrelasjoner
curl -s "http://localhost:8083/testdata/verification/melosys-eessi/saksrelasjoner" | jq .

# Create saksrelasjon manually
curl -X POST "http://localhost:8083/api/sak" \
  -H "Content-Type: application/json" \
  -d '{"gsakSaksnummer": 66, "rinaSaksnummer": "1000001", "bucType": "LA_BUC_03"}'
```

### melosys-api

```bash
# Generate token first!
export MELOSYS_TOKEN=$(curl -s -X POST "http://localhost:8082/isso/token" \
  -d "grant_type=client_credentials&client_id=melosys-api&client_secret=dummy&audience=melosys-localhost" \
  | jq -r '.access_token')

# Get BUCs for behandling
curl -s -H "Authorization: Bearer $MELOSYS_TOKEN" \
  "http://localhost:8080/api/eessi/bucer/{behandlingId}?statuser=UTKAST,AVBRUTT,SENDT,MOTTATT" | jq .
```

### melosys-eessi

```bash
# Generate token first!
export MELOSYS_TOKEN=$(curl -s -X POST "http://localhost:8082/isso/token" \
  -d "grant_type=client_credentials&client_id=melosys-api&client_secret=dummy&audience=melosys-localhost" \
  | jq -r '.access_token')

# Get BUCs for arkivsak
curl -s -H "Authorization: Bearer $MELOSYS_TOKEN" \
  "http://localhost:8081/api/sak/{arkivSakId}/bucer?statuser=UTKAST,AVBRUTT,SENDT,MOTTATT" | jq .

# Hent BUC detaljer
curl -s -H "Authorization: Bearer $MELOSYS_TOKEN" \
  "http://localhost:8081/api/rina/buc/{rinaSakId}" | jq .
```

### eux-rina-api

```bash
# Generate token first!
export EUX_TOKEN=$(curl -s -X POST "http://localhost:8082/isso/token" \
  -d "grant_type=client_credentials&client_id=melosys-eessi&client_secret=dummy&scope=dummy" \
  | jq -r '.access_token')

# Get BUC
curl -s -H "Authorization: Bearer $EUX_TOKEN" \
  "http://localhost:9090/cpi/buc/{rinaSakId}" | jq .

# Get SED
curl -s -H "Authorization: Bearer $EUX_TOKEN" \
  "http://localhost:9090/cpi/buc/{rinaSakId}/sed/{dokumentId}" | jq .

# Get SED as PDF
curl -s -H "Authorization: Bearer $EUX_TOKEN" \
  "http://localhost:9090/cpi/buc/{rinaSakId}/sed/{dokumentId}/pdf" --output sed.pdf

# List all available endpoints
curl -s "http://localhost:9090/v3/api-docs" | jq '.paths | keys'
```

## OAuth Server Details

mock-oauth2-server runs on port 8082 with issuer ID "isso".

| Parameter | Value | Used For |
|-----------|-------|----------|
| `audience=melosys-localhost` | Sets `aud` claim | melosys-api, melosys-eessi |
| `scope=dummy` | Triggers melosys-eessi mapping | eux-rina-api |

Token endpoint: `http://localhost:8082/isso/token`

## Troubleshooting

| Error | Cause | Solution |
|-------|-------|----------|
| JwtTokenUnauthorizedException | Token expired or invalid signature | Generate fresh token |
| 401 Unauthorized | Wrong audience or expired token | Check token claims, regenerate |
| 404 Not Found | Wrong endpoint path or resource missing | Verify endpoint and IDs |
| Connection refused | Service not running | Check `lsof -i :{port}` |
| 500 Method not supported | Wrong HTTP method | Check API docs (GET vs POST) |

### Verify Token Claims

```bash
echo $MELOSYS_TOKEN | cut -d'.' -f2 | base64 -d 2>/dev/null | jq .
```

Expected claims for melosys-api/melosys-eessi:
- `iss`: `http://host.docker.internal:8082/isso`
- `aud`: `melosys-localhost`

## Service Architecture

```
melosys-web (3000)
    ↓
melosys-api (8080) ──→ melosys-mock (8083)
    ↓
melosys-eessi (8081)
    ↓
eux-rina-api (9090)
    ↓
melosys-mock (8083) [RINA CPI: /eessiRest/Cases/*]
```

## Port Reference

| Service | Port | Notes |
|---------|------|-------|
| melosys-api | 8080 | Main backend API |
| melosys-eessi | 8081 | EESSI integration |
| melosys-mock | 8083 | All mocked services |
| mock-oauth2-server | 8082 | OAuth token generation |
| mock-oauth2-server-sts | 8086 | STS tokens (legacy) |
| eux-rina-api | 9090 | RINA CPI wrapper |
