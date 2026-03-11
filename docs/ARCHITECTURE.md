# Arquitetura

## Visão Geral

O Breach Intelligence Platform é uma API REST de threat intelligence que agrega dados de múltiplos provedores para verificação de vazamentos de email e senha.

## Diagrama de Componentes

```
┌─────────────────────────────────────────────────────────────────┐
│                         Cliente (Browser/API)                     │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    FastAPI (API Layer)                           │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌───────────┐ │
│  │ breach-check│ │password-check│ │ auth/api-keys│ │ webhooks  │ │
│  │  /history   │ │/password-hist│ │  /stats     │ │ /metrics  │ │
│  └─────────────┘ └─────────────┘ └─────────────┘ └───────────┘ │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Service Layer                                 │
│  BreachService │ PasswordService │ AuthService │ WebhookService  │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Provider Layer                                │
│     DemoProvider │ HIBPProvider │ LeakCheckProvider              │
└───────────────────────────────┬─────────────────────────────────┘
                                │
        ┌───────────────────────┼───────────────────────┐
        ▼                       ▼                       ▼
┌───────────────┐      ┌───────────────┐      ┌───────────────┐
│   PostgreSQL  │      │     Redis      │      │  APIs Externas │
│   (SQLAlchemy)│      │  (Cache/Broker)│      │  HIBP, LeakCheck│
└───────────────┘      └───────────────┘      └───────────────┘
```

## Fluxo de Verificação de Email

```
1. Request POST /breach-check { email }
2. Validar email
3. Verificar cache Redis (chave: breach_check:{email})
4. Se cache hit → retornar
5. Consultar providers (Demo, HIBP, LeakCheck) em paralelo
6. Deduplicar resultados por nome do vazamento
7. Calcular risk_score (safe/low/medium/high)
8. Salvar em breach_checks + breach_records
9. Gravar no cache (TTL 24h)
10. Se usuário autenticado e com webhooks → notificar
11. Retornar resultado
```

## Fluxo de Verificação de Senha

```
1. Request POST /password-check { password }
2. Hash SHA-1 da senha (local)
3. Enviar apenas prefixo (5 chars) para Pwned Passwords API (k-anonymity)
4. Comparar sufixo localmente com resposta
5. Se autenticado → salvar em password_checks (sem a senha)
6. Retornar { pwned, count }
```

## Autenticação

- **JWT**: Bearer token para sessões de usuário
- **API Key**: Bearer token no formato `bip_*` para acesso programático
- Rate limit por IP ou por API key quando autenticado

## Segurança

- Senhas: bcrypt para hash, nunca armazenadas em texto
- Verificação de senha: k-anonymity (Pwned Passwords) - senha nunca enviada
- API keys: armazenadas como SHA-256, exibidas apenas na criação
- Webhooks: assinatura HMAC-SHA256 no header X-Webhook-Signature
