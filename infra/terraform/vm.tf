# A Azure exige uma chave SSH para VMs Linux, mas a porta 22 é negada no NSG e a chave privada
# não sai do state: o acesso administrativo é só via "az vm run-command".
resource "tls_private_key" "vm" {
  algorithm = "RSA"
  rsa_bits  = 4096
}

resource "azurerm_linux_virtual_machine" "app" {
  name                            = "vm-${local.nome}"
  computer_name                   = local.nome
  resource_group_name             = azurerm_resource_group.rg.name
  location                        = azurerm_resource_group.rg.location
  size                            = var.vm_size
  admin_username                  = "azureuser"
  disable_password_authentication = true
  network_interface_ids           = [azurerm_network_interface.app.id]
  encryption_at_host_enabled      = false
  tags                            = local.tags

  admin_ssh_key {
    username   = "azureuser"
    public_key = tls_private_key.vm.public_key_openssh
  }

  os_disk {
    name                 = "osdisk-${local.nome}"
    caching              = "ReadWrite"
    storage_account_type = "StandardSSD_LRS"
    disk_size_gb         = 30
  }

  source_image_reference {
    publisher = "Canonical"
    offer     = "ubuntu-24_04-lts"
    sku       = "server"
    version   = "latest"
  }

  identity {
    type = "SystemAssigned"
  }

  boot_diagnostics {}

  custom_data = base64encode(templatefile("${path.module}/cloud-init.yaml.tftpl", {
    compose      = file("${path.module}/../../docker-compose.yml")
    fqdn         = local.fqdn
    image_tag    = var.image_tag
    rpa_token    = random_password.rpa_token.result
    robo_token   = random_password.robo_token.result
    metrics_hash = random_password.metrics.bcrypt_hash
  }))

  lifecycle {
    # O pipeline atualiza compose e imagens via run-command; mudar o cloud-init não deve recriar a VM.
    ignore_changes = [custom_data]
  }
}
