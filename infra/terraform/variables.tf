variable "subscription_id" {
  description = "ID da assinatura Azure for Students."
  type        = string
}

variable "location" {
  description = "Região. eastus2 é a mais barata entre as permitidas pela política da assinatura."
  type        = string
  default     = "eastus2"
}

variable "projeto" {
  description = "Prefixo dos recursos."
  type        = string
  default     = "passolivre"
}

variable "dono" {
  description = "Responsável pelos recursos (tag FinOps)."
  type        = string
  default     = "equipe-gs-4es"
}

variable "dns_label" {
  description = "Rótulo DNS do IP público: <dns_label>.<location>.cloudapp.azure.com"
  type        = string
  default     = "passolivre-gs"
}

variable "vm_size" {
  description = "Tamanho da VM (right-sizing: B1s basta para o MVP com SQLite)."
  type        = string
  default     = "Standard_B1s"
}

variable "budget_mensal_usd" {
  description = "Trava de gasto: ao atingir 100% do valor real, a VM é desalocada automaticamente."
  type        = number
  default     = 20
}

variable "budget_inicio" {
  description = "Início do budget (primeiro dia de um mês, formato RFC3339)."
  type        = string
  default     = "2026-11-01T00:00:00Z"
}

variable "budget_emails" {
  description = "E-mails extras para avisos do budget (além do Owner da assinatura)."
  type        = list(string)
  default     = []
}

variable "github_repo" {
  description = "Repositório autorizado a fazer deploy via OIDC (owner/nome)."
  type        = string
  default     = "gustavobrisqui/passo-livre"
}

variable "github_oidc_subject_repo" {
  description = <<-EOT
    Prefixo do "subject" do token OIDC do GitHub. Repositórios novos usam o formato com IDs imutáveis:
    repo:<owner>@<owner_id>/<repo>@<repo_id>  (consulte: gh api repos/<owner>/<repo> --jq '.owner.id, .id')
  EOT
  type        = string
  default     = "repo:gustavobrisqui@127115089/passo-livre@1460691146"
}

variable "image_tag" {
  description = "Tag inicial das imagens no GHCR (o pipeline atualiza a cada deploy)."
  type        = string
  default     = "latest"
}

variable "webhook_expira_em" {
  description = "Validade do webhook do runbook da trava de gasto."
  type        = string
  default     = "2027-11-17T00:00:00Z"
}
