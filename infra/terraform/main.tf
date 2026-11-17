locals {
  nome = var.projeto
  tags = {
    projeto  = "passo-livre"
    ambiente = "producao-mvp"
    dono     = var.dono
    custo    = "gs-fiap-2026"
    iac      = "terraform"
  }
  fqdn = "${var.dns_label}.${var.location}.cloudapp.azure.com"
}

data "azurerm_client_config" "atual" {}

resource "azurerm_resource_group" "rg" {
  name     = "rg-${local.nome}"
  location = var.location
  tags     = local.tags
}

# Segredos gerados pelo Terraform: ficam só no state remoto (fora do Git) e no .env da VM (chmod 600).
resource "random_password" "metrics" {
  length  = 32
  special = false
}

resource "random_password" "rpa_token" {
  length  = 48
  special = false
}

resource "random_password" "robo_token" {
  length  = 48
  special = false
}
