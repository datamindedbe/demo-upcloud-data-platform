#!/usr/bin/env bash

ADMIN_TOKEN=(curl -X POST "https://zitadel.<domain>/oauth/v2/token" \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "grant_type=client_credentials" \
    -d "client_id=" \
    -d "client_secret=" \
    -d "scope=openid")
TRINO_TOKEN=(curl -X POST "https://zitadel.<domain>/oauth/v2/token" \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "grant_type=client_credentials" \
    -d "client_id=trino-opa" \
    -d "client_secret=" \
    -d "scope=openid")

curl -X POST https://lakekeeper.<domain>/management/v1/user \
  -H "Authorization: Bearer <user-to-register-jwt-token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "<name-of-machine-user>",
    "subject": "oidc~<id-of-machine-user>"
  }'

TRINO_USER_ID=$(curl -s https://lakekeeper.<your-domain>/management/v1/user \
    -H "Authorization: Bearer $TOKEN" | jq -r '.users[] | select(.name=="trino-opa") | .id')

curl -X POST "https://lakekeeper.<your-domain>/management/v1/server/grants" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"assignments\": [{\"type\": \"operator\", \"principal\": \"$TRINO_USER_ID\"}]}"

curl -X POST "https://lakekeeper.<your-domain>/management/v1/server/grants" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"assignments\": [{\"type\": \"project_admin\", \"principal\": \"$TRINO_USER_ID\"}]}"