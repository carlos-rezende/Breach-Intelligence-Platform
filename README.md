# Breach Intelligence Platform

[![CI](https://github.com/YOUR_USERNAME/REPO_NAME/actions/workflows/ci.yml/badge.svg)](https://github.com/YOUR_USERNAME/REPO_NAME/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](https://www.docker.com/)

API de threat intelligence para verificação de vazamentos de email e senha, agregando informações de múltiplos provedores.

> **⚠️ Verificação de senhas é real**  
> A detecção de vazamento de senhas utiliza a base de dados **Pwned Passwords** (Have I Been Pwned), com centenas de milhões de senhas expostas em vazamentos reais. O resultado é **verdadeiro** — se sua senha aparecer como vazada, ela realmente foi comprometida em algum incidente de segurança. **Troque imediatamente** qualquer senha que for detectada como vazada.

## Arquitetura

```
┌─────────────────────────────────────────────────────────────┐
│                      API Layer (FastAPI)                     │
├─────────────────────────────────────────────────────────────┤
│  Routes: breach, history, stats, auth, metrics               │
├─────────────────────────────────────────────────────────────┤
│  Service Layer: BreachService, AuthService                  │
├─────────────────────────────────────────────────────────────┤
│  Provider Layer: Demo, HIBP, LeakCheck (plugável)           │
├─────────────────────────────────────────────────────────────┤
│  Data Layer: PostgreSQL, Redis, SQLAlchemy                  │
├─────────────────────────────────────────────────────────────┤
│  Infrastructure: Celery, Alembic, Docker                     │
└─────────────────────────────────────────────────────────────┘
```

## Interface Web

Acesse **http://localhost:8011** para uma interface amigável que permite:
- **Verificar email** – inserir email e ver score de risco + lista de vazamentos
- **Verificar senha** – inserir senha (usa k-anonymity, nunca é enviada) e ver se foi vazada
- Dicas de emails para teste (demo)

## Estrutura do Projeto

```
app/
├── main.py              # Aplicação principal
├── config/              # Configurações
├── core/                # Logging, security, rate limit, dependencies
├── database/            # Session, models
├── schemas/             # Pydantic
├── routes/              # API endpoints (breach, password, auth, api-keys, webhooks)
├── services/            # Lógica de negócio
├── providers/           # Demo, HIBP, LeakCheck
├── workers/             # Celery tasks
├── cache/               # Redis
└── utils/
static/
└── index.html           # Interface web de consulta
docs/
└── ARCHITECTURE.md      # Documentação de arquitetura
```

## Tecnologias

- **Python** 3.12+
- **FastAPI** - API
- **PostgreSQL** - Banco de dados
- **Redis** - Cache e broker Celery
- **Celery** - Fila assíncrona
- **Alembic** - Migrations
- **Docker** - Containerização

## Instalação

### Com Docker

```bash
cp .env.example .env
docker-compose up -d
```

API: http://localhost:8011  
Interface web: http://localhost:8011  
Docs: http://localhost:8011/docs

### Local

```bash
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

Configure PostgreSQL e Redis. Execute:

```bash
alembic upgrade head   # Cria tabelas (inclui password_checks, api_keys, webhooks)
uvicorn app.main:app --reload --port 8011
```

## Endpoints

### POST /breach-check

Verifica se um email apareceu em vazamentos.

```bash
curl -X POST "http://localhost:8011/breach-check" \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@demo.com"}'
```

Resposta:

```json
{
  "email": "admin@demo.com",
  "breached": true,
  "breach_count": 3,
  "breaches": [
    {"name": "LinkedIn", "year": 2012},
    {"name": "Adobe", "year": 2013}
  ],
  "risk_score": "medium",
  "checked_at": "2024-01-01T12:00:00Z"
}
```

### POST /password-check

Verifica se uma senha apareceu em vazamentos (Pwned Passwords - k-anonymity, sem API key).

**A verificação é real:** utiliza dados de vazamentos reais. Se retornar `pwned: true`, a senha foi realmente comprometida — troque-a imediatamente.

```bash
curl -X POST "http://localhost:8011/password-check" \
  -H "Content-Type: application/json" \
  -d '{"password": "password123"}'
```

Resposta:

```json
{
  "pwned": true,
  "count": 2387321,
  "checked_at": "2024-01-01T12:00:00Z"
}
```

### GET /history/{email}

Histórico de verificações.

```bash
curl "http://localhost:8011/history/admin@demo.com"
```

### GET /stats

Estatísticas da plataforma.

```bash
curl "http://localhost:8011/stats"
```

### GET /health

Health check: API, PostgreSQL, Redis, Celery.

```bash
curl "http://localhost:8011/health"
```

### POST /auth/register

Registro de usuário.

```bash
curl -X POST "http://localhost:8011/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "senha12345"}'
```

### POST /auth/login

Login com JWT.

```bash
curl -X POST "http://localhost:8011/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "senha12345"}'
```

### GET /password-history

Histórico de verificações de senha (requer autenticação). Não armazena a senha.

```bash
curl -H "Authorization: Bearer <token>" "http://localhost:8011/password-history"
```

### POST /auth/api-keys

Cria API key para acesso programático (requer autenticação).

```bash
curl -X POST "http://localhost:8011/auth/api-keys" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"name": "Minha API Key"}'
```

### GET /auth/api-keys

Lista API keys do usuário.

### POST /auth/webhooks

Registra webhook para notificações quando verificar email (autenticado).

### GET /metrics

Métricas Prometheus.

```bash
curl "http://localhost:8011/metrics"
```

## Providers

| Provider | Descrição | Configuração |
|----------|-----------|--------------|
| **Demo** | Simula vazamentos | Sempre ativo |
| **HIBP** | Have I Been Pwned | `HIBP_API_KEY` (opcional) |
| **LeakCheck** | API pública gratuita | Sempre ativo (sem API key) |

## Como testar a verificação de vazamentos

### 1. Provider Demo (sem configuração)

Funciona imediatamente, sem API key:

```bash
# 3 vazamentos simulados (LinkedIn, Adobe, Demo Corp)
curl -X POST "http://localhost:8011/breach-check" \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@demo.com"}'

# 2 vazamentos simulados (Gawker, Stratfor)
curl -X POST "http://localhost:8011/breach-check" \
  -H "Content-Type: application/json" \
  -d '{"email": "test@demo.com"}'
```

### 2. HIBP com API key de teste

Para testar a integração com Have I Been Pwned sem custo:

1. No `.env`, defina:
   ```
   HIBP_API_KEY=00000000000000000000000000000000
   ```

2. Reinicie a API e teste com os emails oficiais de teste do HIBP:
   ```bash
   curl -X POST "http://localhost:8011/breach-check" \
     -H "Content-Type: application/json" \
     -d '{"email": "account-exists@hibp-integration-tests.com"}'
   ```

   Outros emails de teste: `spam-list-only@hibp-integration-tests.com`, `stealer-log@hibp-integration-tests.com`

### 3. HIBP com API key real

Para consultar vazamentos reais de qualquer email:

1. Obtenha sua chave em: https://haveibeenpwned.com/API/Key
2. Configure no `.env`:
   ```
   HIBP_API_KEY=sua_chave_aqui
   ```
3. Reinicie a API e consulte qualquer email.

**Interface web:** Acesse http://localhost:8011 para uma interface amigável de consulta (formulário + exibição de resultados).

## Emails de Demo

| Email | Vazamentos |
|-------|------------|
| `admin@demo.com` | 3 (LinkedIn, Adobe, Demo Corp) |
| `test@demo.com` | 2 (Gawker, Stratfor) |

## Score de Risco

| Vazamentos | Score |
|------------|-------|
| 0 | safe |
| 1-2 | low |
| 3-5 | medium |
| 6+ | high |

## Testes

```bash
TESTING=1 pytest tests/ -v
```
