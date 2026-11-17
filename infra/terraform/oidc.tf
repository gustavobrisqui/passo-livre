# Deploy sem segredo de longa duração: o GitHub Actions troca o token OIDC do workflow
# por um token da Azure. A identidade só pode agir sobre a VM do projeto (mínimo privilégio).
resource "azuread_application" "github" {
  display_name = "github-${local.nome}-deploy"
  owners       = [data.azurerm_client_config.atual.object_id]
}

resource "azuread_service_principal" "github" {
  client_id = azuread_application.github.client_id
  owners    = [data.azurerm_client_config.atual.object_id]
}

resource "azuread_application_federated_identity_credential" "main" {
  application_id = azuread_application.github.id
  display_name   = "github-main"
  description    = "Push na branch main de ${var.github_repo}"
  audiences      = ["api://AzureADTokenExchange"]
  issuer         = "https://token.actions.githubusercontent.com"
  subject        = "repo:${var.github_repo}:ref:refs/heads/main"
}

resource "azuread_application_federated_identity_credential" "producao" {
  application_id = azuread_application.github.id
  display_name   = "github-env-production"
  description    = "Jobs no environment production de ${var.github_repo}"
  audiences      = ["api://AzureADTokenExchange"]
  issuer         = "https://token.actions.githubusercontent.com"
  subject        = "repo:${var.github_repo}:environment:production"
}

# "Virtual Machine Contributor" no escopo da VM: permite run-command (deploy) e nada fora dela.
resource "azurerm_role_assignment" "github_vm" {
  scope                = azurerm_linux_virtual_machine.app.id
  role_definition_name = "Virtual Machine Contributor"
  principal_id         = azuread_service_principal.github.object_id
}
