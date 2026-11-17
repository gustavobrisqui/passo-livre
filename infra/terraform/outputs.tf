output "url" {
  description = "URL pública do MVP."
  value       = "https://${local.fqdn}"
}

output "resource_group" {
  value = azurerm_resource_group.rg.name
}

output "vm_name" {
  value = azurerm_linux_virtual_machine.app.name
}

output "ip_publico" {
  value = azurerm_public_ip.app.ip_address
}

# Valores para os GitHub Secrets do deploy via OIDC (não são segredos, mas ficam em Secrets por boa prática).
output "azure_client_id" {
  value = azuread_application.github.client_id
}

output "azure_tenant_id" {
  value = data.azurerm_client_config.atual.tenant_id
}

output "azure_subscription_id" {
  value = var.subscription_id
}

output "webhook_trava_gasto" {
  description = "Webhook do runbook (para testar a trava manualmente). Sensível."
  value       = azurerm_automation_webhook.desligar_vm.uri
  sensitive   = true
}

output "rpa_token" {
  value     = random_password.rpa_token.result
  sensitive = true
}

output "robo_token" {
  value     = random_password.robo_token.result
  sensitive = true
}

output "metrics_password" {
  value     = random_password.metrics.result
  sensitive = true
}
