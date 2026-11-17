# ------------------------------------------------------------------------------------------
# TRAVA DE GASTO (US$ 20)
# Budgets da Azure só AVISAM; não bloqueiam. Para virar trava de verdade:
#   budget (100% real) -> Action Group -> webhook -> runbook (Azure Automation) -> desaloca a VM.
# VM desalocada não cobra computação. Os custos chegam ao Cost Management com 8-24h de atraso,
# por isso há avisos antecipados em 50%, 80% e 100% previsto.
# ------------------------------------------------------------------------------------------

resource "azurerm_automation_account" "finops" {
  name                          = "aa-${local.nome}-finops"
  location                      = azurerm_resource_group.rg.location
  resource_group_name           = azurerm_resource_group.rg.name
  sku_name                      = "Basic"
  public_network_access_enabled = true
  local_authentication_enabled  = true
  tags                          = local.tags

  identity {
    type = "SystemAssigned"
  }
}

# O runbook só pode mexer na VM do projeto.
resource "azurerm_role_assignment" "finops_vm" {
  scope                = azurerm_linux_virtual_machine.app.id
  role_definition_name = "Virtual Machine Contributor"
  principal_id         = azurerm_automation_account.finops.identity[0].principal_id
}

resource "azurerm_automation_runbook" "desligar_vm" {
  name                    = "Desalocar-VM-Passo-Livre"
  location                = azurerm_resource_group.rg.location
  resource_group_name     = azurerm_resource_group.rg.name
  automation_account_name = azurerm_automation_account.finops.name
  runbook_type            = "PowerShell"
  log_verbose             = false
  log_progress            = false
  description             = "Trava de gasto: desaloca a VM quando o budget atinge 100%."
  tags                    = local.tags

  content = templatefile("${path.module}/runbook-desalocar-vm.ps1.tftpl", {
    vm_id = azurerm_linux_virtual_machine.app.id
  })
}

resource "azurerm_automation_webhook" "desligar_vm" {
  name                    = "budget-100"
  resource_group_name     = azurerm_resource_group.rg.name
  automation_account_name = azurerm_automation_account.finops.name
  runbook_name            = azurerm_automation_runbook.desligar_vm.name
  expiry_time             = var.webhook_expira_em
  enabled                 = true
}

resource "azurerm_monitor_action_group" "finops" {
  name                = "ag-${local.nome}-finops"
  resource_group_name = azurerm_resource_group.rg.name
  short_name          = "plfinops"
  tags                = local.tags

  automation_runbook_receiver {
    name                    = "desalocar-vm"
    automation_account_id   = azurerm_automation_account.finops.id
    runbook_name            = azurerm_automation_runbook.desligar_vm.name
    webhook_resource_id     = azurerm_automation_webhook.desligar_vm.id
    is_global_runbook       = false
    service_uri             = azurerm_automation_webhook.desligar_vm.uri
    use_common_alert_schema = true
  }
}

resource "azurerm_consumption_budget_resource_group" "trava" {
  name              = "budget-${local.nome}-${var.budget_mensal_usd}usd"
  resource_group_id = azurerm_resource_group.rg.id
  amount            = var.budget_mensal_usd
  time_grain        = "Monthly"

  time_period {
    start_date = var.budget_inicio
  }

  notification {
    enabled        = true
    threshold      = 50
    operator       = "GreaterThanOrEqualTo"
    threshold_type = "Actual"
    contact_roles  = ["Owner"]
    contact_emails = var.budget_emails
  }

  notification {
    enabled        = true
    threshold      = 80
    operator       = "GreaterThanOrEqualTo"
    threshold_type = "Actual"
    contact_roles  = ["Owner"]
    contact_emails = var.budget_emails
  }

  notification {
    enabled        = true
    threshold      = 100
    operator       = "GreaterThanOrEqualTo"
    threshold_type = "Forecasted"
    contact_roles  = ["Owner"]
    contact_emails = var.budget_emails
  }

  # 100% REAL: além do e-mail, dispara o runbook que desaloca a VM.
  notification {
    enabled        = true
    threshold      = 100
    operator       = "GreaterThanOrEqualTo"
    threshold_type = "Actual"
    contact_roles  = ["Owner"]
    contact_emails = var.budget_emails
    contact_groups = [azurerm_monitor_action_group.finops.id]
  }

  lifecycle {
    ignore_changes = [time_period]
  }
}
