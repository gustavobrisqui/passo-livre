#!/usr/bin/env bash
# Bootstrap (uma vez): registra provedores da assinatura e cria o Storage do state remoto do Terraform.
# Gera infra/terraform/backend.hcl (ignorado pelo Git).
set -euo pipefail
cd "$(dirname "$0")"

LOCATION="${LOCATION:-eastus2}"
RG="rg-passolivre-tfstate"
CONTAINER="tfstate"

for ns in Microsoft.Compute Microsoft.Network Microsoft.Storage Microsoft.Automation \
          Microsoft.Consumption Microsoft.Insights Microsoft.ManagedIdentity; do
  az provider register --namespace "$ns" --only-show-errors >/dev/null
done

az group create -n "$RG" -l "$LOCATION" \
  --tags projeto=passo-livre ambiente=tfstate custo=gs-fiap-2026 iac=bootstrap -o none

SA="$(az storage account list -g "$RG" --query "[0].name" -o tsv)"
if [[ -z "$SA" ]]; then
  SA="passolivretf$(openssl rand -hex 3)"
  az storage account create -n "$SA" -g "$RG" -l "$LOCATION" \
    --sku Standard_LRS --kind StorageV2 --min-tls-version TLS1_2 \
    --allow-blob-public-access false --https-only true \
    --tags projeto=passo-livre ambiente=tfstate custo=gs-fiap-2026 -o none
fi
az storage account blob-service-properties update -n "$SA" -g "$RG" --enable-versioning true -o none
az storage container create -n "$CONTAINER" --account-name "$SA" --auth-mode key -o none

cat > terraform/backend.hcl <<EOF
resource_group_name  = "$RG"
storage_account_name = "$SA"
container_name       = "$CONTAINER"
key                  = "passolivre.tfstate"
EOF
echo "OK: state remoto em $SA/$CONTAINER (backend.hcl gerado)."
