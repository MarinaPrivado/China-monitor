# Especificação: Agente de Monitoramento de Inscrições na China

## Objetivo
Agente IA que monitora 1-6 sites de intercâmbio e mestrados/pós-graduação na China, identifica datas de inscrição (abertas/fechadas) e envia relatório semanal por e-mail.

---

## Arquitetura

```
┌─────────────┐     ┌──────────────┐     ┌───────────┐     ┌──────────┐
│  Scrapers   │────▶│  Parser IA   │────▶│  Parser   │────▶│  Email   │
│  (1-6 sites)│     │  (LLM)       │     │  JSON     │     │  Semanal │
└─────────────┘     └──────────────┘     └───────────┘     └──────────┘
                           │
                     ┌─────▼─────┐
                     │  Histórico│
                     │  (data/)  │
                     └───────────┘
```

---

## Componentes

### 1. Scrapper (`scraper.py`)
- Visita cada site configurado
- Usa Playwright (sites com JS) + requests fallback
- Extrai texto bruto da página (títulos, tabelas, listas, parágrafos)
- Respeita `robots.txt` e delays entre requisições
- Salva HTML raw em `data/raw/YYYY-MM-DD/`

### 2. Parser IA (`llm_parser.py`)
- Envia HTML/texto para LLM com prompt estruturado
- **Prompt exemplo:**
  ```
  Analise o conteúdo abaixo de um site sobre programas na China.
  Extraia TODAS as datas de inscrição mencionadas.
  Para cada inscrição, retorne JSON:
  - program_name: nome do programa
  - type: "intercambio" | "mestrado" | "pos-graduacao"
  - status: "aberta" | "fechada" | "em-breve"
  - open_date: data de abertura (YYYY-MM-DD ou null)
  - close_date: data de encerramento (YYYY-MM-DD ou null)
  - deadline: prazo final (YYYY-MM-DD ou null)
  - url: link da página de inscrição
  - notes: observações extras
  ```
- Usa `gpt-4o-mini` (custo baixo) ou `gpt-4o` (precisão maior)

### 3. Comparador (`comparator.py`)
- Compara resultados da semana anterior com atual
- Detecta: novas inscrições, inscrições que fecharam, datas alteradas
- Salva histórico em `data/results/YYYY-MM-DD.json`

### 4. Email Sender (`email_sender.py`)
- Envia relatório semanal toda **segunda às 9h**
- Template HTML bonito com tabela colorida:
  - 🟢 Verde = inscrições abertas
  - 🔴 Vermelho = inscrições fechadas
  - 🟡 Amarelo = em breve
- Usa SMTP (Gmail, Outlook, etc.)

### 5. Scheduler (`scheduler.py`)
- Executa o pipeline completo: scrap → LLM → compara → (email semanal)
- Roda via cron/celery/task-scheduler ou loop com `schedule` lib
- Verificação dos sites: a cada 24h (configurável)
- Email: toda segunda-feira

---

## Configuração (`config.json`)

```json
{
  "sites": [
    "https://campuschina.org",
    "https://www.csc.edu.cn",
    "https://en.unist.cn",
    "https://www.topuniversities.com",
    "https://www.scholarships.com",
    "https://studyinchina.csc.edu.cn"
  ],
  "program_types": ["intercambio", "mestrado", "pos-graduacao"],
  "check_interval_hours": 24,
  "email": {
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "sender_email": "seu-email@gmail.com",
    "sender_password": "",
    "recipient_email": "seu-email@gmail.com"
  },
  "llm": {
    "provider": "openai",
    "api_key": "",
    "model": "gpt-4o-mini",
    "max_tokens": 2000
  },
  "schedule": {
    "check_days": ["seg", "ter", "qua", "qui", "sex", "sab", "dom"],
    "email_day": "seg",
    "email_time": "09:00"
  }
}
```

---

## Estrutura de Arquivos

```
china-monitor/
├── config.json           # Configurações
├── requirements.txt      # Dependências
├── main.py              # Entry point
├── scraper.py           # Web scraping
├── llm_parser.py        # Parser com IA
├── comparator.py        # Compara resultados
├── email_sender.py      # Envio de emails
├── scheduler.py         # Agendamento
├── templates/
│   └── email.html       # Template do email
└── data/
    ├── raw/             # HTMLs brutos por data
    └── results/         # JSONs processados por data
```

---

## Output do Email (exemplo)

| Programa | Tipo | Status | Abertura | Encerramento | Prazo | Link |
|----------|------|--------|----------|--------------|-------|------|
| CSC Scholarship | Mestrado | 🟢 Aberta | 2026-01-15 | 2026-03-31 | 2026-03-31 | [link] |
| PKU Exchange | Intercâmbio | 🔴 Fechada | 2025-10-01 | 2025-11-30 | 2025-11-30 | [link] |
| Tsinghua PhD | Pós | 🟡 Em breve | 2026-06-01 | - | 2026-07-15 | [link] |

---

## Tecnologias

| Componente | Tecnologia |
|------------|------------|
| Scraping | Playwright + BeautifulSoup |
| IA | OpenAI API (gpt-4o-mini) |
| Scheduler | `schedule` library ou Windows Task Scheduler |
| Email | `smtplib` (Python stdlib) |
| HTML Parse | BeautifulSoup4 |
| HTTP | requests + aiohttp |

---

## Dependências (`requirements.txt`)

```
playwright>=1.40
beautifulsoup4>=4.12
requests>=2.31
openai>=1.10
schedule>=1.2
jinja2>=3.1
python-dotenv>=1.0
```

---

## Fluxo de Execução

1. **A cada 24h:** scraper visita sites → extrai conteúdo → salva raw
2. **Imediatamente após:** LLM analisa conteúdo → extrai datas/status → salva JSON
3. **Comparador:** verifica mudanças vs semana anterior → atualiza histórico
4. **Toda segunda às 9h:** gera email com todas inscrições → envia para destinatário

---

## Tratamento de Erros

- Site fora do ar → log + retry 3x com delay → pula se falhar
- LLM retorna JSON inválido → retry até 3x
- SMTP falha → log + retry na próxima execução
- Sem resultados → não envia email (ou envia "nenhuma inscrição encontrada")

---

## Próximos Passos para Implementação

1. Definir os 1-6 sites exatos para monitorar
2. Configurar credenciais de email (SMTP)
3. Configurar API key da OpenAI (ou alternativa: Anthropic, Groq)
4. Implementar scraper por site (cada site pode precisar de abordagem diferente)
5. Testar pipeline completo
6. Configurar agendamento no Windows Task Scheduler
