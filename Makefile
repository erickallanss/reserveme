.PHONY: help install setup up down restart build clean logs migrate makemigrations shell test test-cov lint format check

# Variáveis
DOCKER_COMPOSE = docker compose
DOCKER_EXEC = $(DOCKER_COMPOSE) exec web
PYTHON = python
UV = uv

# Cores para output
GREEN = \033[0;32m
YELLOW = \033[0;33m
RED = \033[0;31m
NC = \033[0m # No Color

help: ## Mostra esta mensagem de ajuda
	@echo "$(GREEN)ReserveMe - Comandos Disponíveis:$(NC)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-20s$(NC) %s\n", $$1, $$2}'
	@echo ""

# ============================================================================
# Setup & Instalação
# ============================================================================

install: ## Instala dependências localmente com uv
	@echo "$(GREEN)📦 Instalando dependências com uv...$(NC)"
	$(UV) pip install --system -e ".[test]"

setup: ## Setup completo: build, up, migrate
	@echo "$(GREEN)🚀 Configurando projeto...$(NC)"
	@$(MAKE) build
	@$(MAKE) up
	@echo "$(YELLOW)⏳ Aguardando containers iniciarem...$(NC)"
	@sleep 5
	@$(MAKE) migrate
	@echo "$(GREEN)✅ Setup completo!$(NC)"
	@echo "$(YELLOW)📝 Acesse: http://localhost:8000/api/docs/$(NC)"

server: ## Build, cria migrations, migra e sobe servidor
	@echo "$(GREEN)🚀 Iniciando servidor completo...$(NC)"
	@echo "$(GREEN)🔨 1/4 - Building containers...$(NC)"
	@$(DOCKER_COMPOSE) build
	@echo "$(GREEN)⬆️  2/4 - Subindo containers...$(NC)"
	@$(DOCKER_COMPOSE) up -d
	@echo "$(YELLOW)⏳ Aguardando containers iniciarem...$(NC)"
	@sleep 5
	@echo "$(GREEN)📝 3/4 - Criando migrations...$(NC)"
	@$(DOCKER_EXEC) $(PYTHON) manage.py makemigrations
	@echo "$(GREEN)📊 4/4 - Aplicando migrations...$(NC)"
	@$(DOCKER_EXEC) $(PYTHON) manage.py migrate
	@echo "$(GREEN)✅ Servidor rodando!$(NC)"
	@echo ""
	@echo "$(YELLOW)🌐 API: http://localhost:8000$(NC)"
	@echo "$(YELLOW)📚 Docs: http://localhost:8000/api/docs/$(NC)"
	@echo "$(YELLOW)📧 Mailpit: http://localhost:8025$(NC)"
	@echo ""
	@echo "$(GREEN)Para ver logs: make logs$(NC)"

# ============================================================================
# Docker
# ============================================================================

build: ## Build dos containers Docker
	@echo "$(GREEN)🔨 Building containers...$(NC)"
	$(DOCKER_COMPOSE) build

up: ## Sobe os containers
	@echo "$(GREEN)⬆️  Subindo containers...$(NC)"
	$(DOCKER_COMPOSE) up -d

down: ## Para os containers
	@echo "$(YELLOW)⬇️  Parando containers...$(NC)"
	$(DOCKER_COMPOSE) down

restart: ## Reinicia os containers
	@echo "$(YELLOW)🔄 Reiniciando containers...$(NC)"
	@$(MAKE) down
	@$(MAKE) up

clean: ## Remove containers, volumes e imagens
	@echo "$(RED)🧹 Limpando containers, volumes e imagens...$(NC)"
	$(DOCKER_COMPOSE) down -v --rmi local

logs: ## Mostra logs dos containers
	$(DOCKER_COMPOSE) logs -f

logs-web: ## Mostra logs do container web
	$(DOCKER_COMPOSE) logs -f web

logs-celery: ## Mostra logs do Celery
	$(DOCKER_COMPOSE) logs -f celery

logs-celery-beat: ## Mostra logs do Celery Beat
	$(DOCKER_COMPOSE) logs -f celery-beat

# ============================================================================
# Django
# ============================================================================

migrate: ## Executa migrations
	@echo "$(GREEN)📊 Executando migrations...$(NC)"
	$(DOCKER_EXEC) $(PYTHON) manage.py migrate

makemigrations: ## Cria novas migrations
	@echo "$(GREEN)📝 Criando migrations...$(NC)"
	$(DOCKER_EXEC) $(PYTHON) manage.py makemigrations

shell: ## Abre Django shell
	$(DOCKER_EXEC) $(PYTHON) manage.py shell

shell-plus: ## Abre Django shell_plus (se instalado)
	$(DOCKER_EXEC) $(PYTHON) manage.py shell_plus

dbshell: ## Abre shell do PostgreSQL
	$(DOCKER_EXEC) $(PYTHON) manage.py dbshell

createsuperuser: ## Cria superusuário Django
	$(DOCKER_EXEC) $(PYTHON) manage.py createsuperuser

collectstatic: ## Coleta arquivos estáticos
	$(DOCKER_EXEC) $(PYTHON) manage.py collectstatic --noinput

check: ## Verifica problemas no projeto Django
	@echo "$(GREEN)🔍 Verificando projeto...$(NC)"
	$(DOCKER_EXEC) $(PYTHON) manage.py check

# ============================================================================
# Testes
# ============================================================================

test: ## Roda todos os testes
	@echo "$(GREEN)🧪 Executando testes...$(NC)"
	$(DOCKER_EXEC) $(PYTHON) -m pytest -v

test-cov: ## Roda testes com cobertura
	@echo "$(GREEN)🧪 Executando testes com cobertura...$(NC)"
	$(DOCKER_EXEC) $(PYTHON) -m pytest -v --cov=reserveme --cov-report=html --cov-report=term-missing

test-unit: ## Roda apenas testes unitários
	@echo "$(GREEN)🧪 Executando testes unitários...$(NC)"
	$(DOCKER_EXEC) $(PYTHON) -m pytest -v reserveme/tests/unit/

test-integration: ## Roda apenas testes de integração
	@echo "$(GREEN)🧪 Executando testes de integração...$(NC)"
	$(DOCKER_EXEC) $(PYTHON) -m pytest -v reserveme/tests/integration/

test-auth: ## Roda testes de autenticação
	@echo "$(GREEN)🧪 Executando testes de autenticação...$(NC)"
	$(DOCKER_EXEC) $(PYTHON) -m pytest -v reserveme/tests/ -k auth

test-watch: ## Roda testes em modo watch
	$(DOCKER_EXEC) $(PYTHON) -m pytest -v --looponfail

# ============================================================================
# Linting & Formatação
# ============================================================================

lint: ## Verifica código com flake8/ruff
	@echo "$(GREEN)🔍 Verificando código...$(NC)"
	$(DOCKER_EXEC) $(PYTHON) -m flake8 reserveme/ core/ || true
	$(DOCKER_EXEC) $(PYTHON) -m ruff check reserveme/ core/ || true

format: ## Formata código com black
	@echo "$(GREEN)🎨 Formatando código...$(NC)"
	$(DOCKER_EXEC) $(PYTHON) -m black reserveme/ core/ || true

# ============================================================================
# Banco de Dados
# ============================================================================

db-reset: ## CUIDADO: Reseta o banco de dados (apaga tudo)
	@echo "$(RED)⚠️  ATENÇÃO: Isso irá apagar TODOS os dados!$(NC)"
	@read -p "Tem certeza? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		echo "$(RED)🗑️  Resetando banco de dados...$(NC)"; \
		$(MAKE) down; \
		docker volume rm test_postgres_data || true; \
		$(MAKE) up; \
		sleep 5; \
		$(MAKE) migrate; \
		echo "$(GREEN)✅ Banco resetado!$(NC)"; \
	fi

db-backup: ## Faz backup do banco de dados
	@echo "$(GREEN)💾 Criando backup...$(NC)"
	@mkdir -p backups
	$(DOCKER_COMPOSE) exec -T db pg_dump -U reserveme reserveme > backups/backup_$$(date +%Y%m%d_%H%M%S).sql
	@echo "$(GREEN)✅ Backup criado em backups/$(NC)"

db-restore: ## Restaura backup do banco (especificar BACKUP=arquivo.sql)
	@if [ -z "$(BACKUP)" ]; then \
		echo "$(RED)❌ Especifique o arquivo: make db-restore BACKUP=arquivo.sql$(NC)"; \
		exit 1; \
	fi
	@echo "$(YELLOW)📥 Restaurando backup $(BACKUP)...$(NC)"
	cat $(BACKUP) | $(DOCKER_COMPOSE) exec -T db psql -U reserveme reserveme
	@echo "$(GREEN)✅ Backup restaurado!$(NC)"

# ============================================================================
# Utilitários
# ============================================================================

ps: ## Lista containers rodando
	$(DOCKER_COMPOSE) ps

stats: ## Mostra estatísticas dos containers
	docker stats $$(docker ps --filter name=test -q)

mailpit: ## Abre Mailpit no navegador
	@echo "$(GREEN)📧 Abrindo Mailpit...$(NC)"
	@xdg-open http://localhost:8025 2>/dev/null || open http://localhost:8025 2>/dev/null || echo "$(YELLOW)Acesse: http://localhost:8025$(NC)"

api-docs: ## Abre documentação da API no navegador
	@echo "$(GREEN)📚 Abrindo API Docs...$(NC)"
	@xdg-open http://localhost:8000/api/docs/ 2>/dev/null || open http://localhost:8000/api/docs/ 2>/dev/null || echo "$(YELLOW)Acesse: http://localhost:8000/api/docs/$(NC)"

version: ## Mostra versões das ferramentas
	@echo "$(GREEN)📋 Versões:$(NC)"
	@echo "Python: $$($(DOCKER_EXEC) $(PYTHON) --version 2>&1)"
	@echo "Django: $$($(DOCKER_EXEC) $(PYTHON) -c 'import django; print(django.get_version())')"
	@echo "PostgreSQL: $$($(DOCKER_COMPOSE) exec db psql --version)"
	@echo "Redis: $$($(DOCKER_COMPOSE) exec redis redis-server --version)"

# Default target
.DEFAULT_GOAL := help
