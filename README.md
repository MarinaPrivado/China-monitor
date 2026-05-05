# China-monitor

Agente de IA que monitora sites de intercâmbio e mestrados/pós-graduação na China, identifica datas de inscrição e envia relatório semanal por email.

## Programas Monitorados

1. **Instituto Confúcio - Intercâmbio**
2. **BRICS Program / Summer School**
3. **Programa Brasil-China de Líderes em Inovação**
4. **Bolsas do Governo Chinês (CSC)**

## Instalação

```bash
pip install -r requirements.txt
playwright install chromium
```

## Configuração

Edite `config.json`:

```json
{
  "llm": {
    "provider": "openrouter",
    "api_key": "sk-or-v1-sua-openrouter-key",
    "model": "meta-llama/llama-3.3-70b-instruct:free"
  },
  "email": {
    "method": "resend",
    "api_key": "re_sua-api-key",
    "from_email": "seu-email@dominio.com",
    "to_email": "destino@email.com"
  }
}
```

**Email via Resend (sem senha):**
1. Acesse https://resend.com/signup (gratis, 3k emails/mes)
2. Crie API Key em Settings -> API Keys
3. Em Domains, adicione seu dominio ou use `onboarding@resend.dev` para testes

Modelos **free** recomendados OpenRouter:
- `meta-llama/llama-3.3-70b-instruct:free` (padrão, melhor qualidade)
- `google/gemini-2.0-flash-exp:free`
- `meta-llama/llama-3.1-8b-instruct:free`
- `mistralai/mistral-7b-instruct:free`
- `deepseek/deepseek-chat-v3-0324:free`

## Uso

**Executar uma vez:**
```bash
python main.py --once
```

**Executar uma vez com email:**
```bash
python main.py --once --email
```

**Executar em modo contínuo (verificação a cada 24h + email semanal):**
```bash
python main.py
```

## Estrutura

```
china-monitor/
├── config.json           # Configurações
├── main.py              # Entry point
├── scraper.py           # Web scraping
├── llm_parser.py        # Parser com IA
├── comparator.py        # Compara resultados
├── email_sender.py      # Envio de emails
├── scheduler.py         # Agendamento
└── data/
    ├── raw/             # HTMLs brutos
    └── results/         # JSONs processados
```
