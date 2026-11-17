terraform {
  required_version = ">= 1.9.0"

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 4.0"
    }
    azuread = {
      source  = "hashicorp/azuread"
      version = "~> 3.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.6"
    }
    tls = {
      source  = "hashicorp/tls"
      version = "~> 4.0"
    }
  }

  # State remoto em Azure Storage (fora do repositório). Configuração parcial:
  # os valores vêm de backend.hcl, gerado por infra/bootstrap-state.sh e ignorado pelo Git.
  #   terraform init -backend-config=backend.hcl
  backend "azurerm" {}
}

provider "azurerm" {
  features {
    virtual_machine {
      delete_os_disk_on_deletion = true
    }
  }
  subscription_id = var.subscription_id
  # Os provedores necessários são registrados pelo bootstrap (assinatura Azure for Students).
  resource_provider_registrations = "none"
}

provider "azuread" {}
