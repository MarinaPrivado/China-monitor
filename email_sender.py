import json
import os
import requests
from datetime import datetime
from jinja2 import Template
from dotenv import load_dotenv

load_dotenv()

TEMPLATES_DIR = os.path.join("templates")
os.makedirs(TEMPLATES_DIR, exist_ok=True)

EMAIL_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <style>
    body { font-family: Arial, sans-serif; background: #f5f5f5; padding: 20px; }
    .container { max-width: 800px; margin: 0 auto; background: #fff; padding: 24px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
    h1 { color: #1a1a1a; border-bottom: 3px solid #de2910; padding-bottom: 10px; }
    h2 { color: #333; margin-top: 24px; }
    table { width: 100%; border-collapse: collapse; margin: 16px 0; }
    th { background: #1a1a1a; color: #fff; padding: 10px; text-align: left; font-size: 13px; }
    td { padding: 10px; border-bottom: 1px solid #eee; font-size: 13px; }
    .aberta { color: #16a34a; font-weight: bold; }
    .fechada { color: #dc2626; font-weight: bold; }
    .em-breve { color: #ca8a04; font-weight: bold; }
    .badge { display: inline-block; padding: 3px 10px; border-radius: 12px; font-size: 11px; font-weight: bold; }
    .badge.aberta { background: #dcfce7; color: #16a34a; }
    .badge.fechada { background: #fee2e2; color: #dc2626; }
    .badge.em-breve { background: #fef9c3; color: #a16207; }
    .footer { margin-top: 32px; padding-top: 16px; border-top: 1px solid #eee; color: #888; font-size: 12px; text-align: center; }
    a { color: #de2910; }
  </style>
</head>
<body>
<div class="container">
  <h1>&#x1F1E8;&#x1F1F3; Monitor de Inscricoes China - {{ date }}</h1>
  <p>Relatorio semanal de oportunidades de intercambio, mestrado e pos-graduacao na China.</p>

  <h2>&#x1F4CB; Todas as Inscricoes</h2>
  <table>
    <tr>
      <th>Programa</th>
      <th>Tipo</th>
      <th>Status</th>
      <th>Abertura</th>
      <th>Encerramento</th>
      <th>Prazo</th>
      <th>Fonte</th>
    </tr>
    {% for p in programs %}
    <tr class="{{ p.status }}">
      <td><strong>{{ p.program_name }}</strong>{% if p.notes %}<br><small style="color:#888">{{ p.notes }}</small>{% endif %}</td>
      <td>{{ p.type }}</td>
      <td><span class="badge {{ p.status }}">{{ p.status | upper }}</span></td>
      <td>{{ p.open_date or "-" }}</td>
      <td>{{ p.close_date or "-" }}</td>
      <td>{{ p.deadline or "-" }}</td>
      <td>{% if p.source_url %}<a href="{{ p.source_url }}">{{ p.source_site }}</a>{% else %}{{ p.source_site }}{% endif %}</td>
    </tr>
    {% endfor %}
  </table>

  {% if new_programs %}
  <h2>&#x1F195; Novas Inscricoes</h2>
  <ul>
    {% for p in new_programs %}
    <li><strong>{{ p.program_name }}</strong> - {{ p.type }} (status: {{ p.status }})</li>
    {% endfor %}
  </ul>
  {% endif %}

  {% if changed %}
  <h2>&#x1F504; Alteracoes</h2>
  <ul>
    {% for c in changed %}
    <li><strong>{{ c.program.program_name }}</strong>: {{ c.old_status }} -> {{ c.new_status }}</li>
    {% endfor %}
  </ul>
  {% endif %}

  {% if closed_programs %}
  <h2>&#x1F6AB; Inscricoes Fechadas</h2>
  <ul>
    {% for p in closed_programs %}
    <li><strong>{{ p.program_name }}</strong></li>
    {% endfor %}
  </ul>
  {% endif %}

  <div class="footer">
    Gerado automaticamente por China Monitor | {{ date }}
  </div>
</div>
</body>
</html>
"""


def render_email(programs, new_programs, changed, closed_programs):
    date_str = datetime.now().strftime("%d/%m/%Y")
    template = Template(EMAIL_TEMPLATE)
    return template.render(
        date=date_str,
        programs=programs,
        new_programs=new_programs,
        changed=changed,
        closed_programs=closed_programs,
    )


def send_email(config, programs, new_programs, changed, closed_programs):
    email_config = config["email"]

    api_key = os.getenv("RESEND_API_KEY") or email_config.get("api_key")

    if not api_key or not email_config.get("to_email"):
        print("[EMAIL] Configuracao de email incompleta. Pulando envio.")
        return False

    html = render_email(programs, new_programs, changed, closed_programs)

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    data = {
        "from": f"China Monitor <{email_config['from_email']}>",
        "to": [email_config["to_email"]],
        "subject": f"China Monitor - Relatorio Semanal ({datetime.now().strftime('%d/%m/%Y')})",
        "html": html,
    }

    try:
        resp = requests.post("https://api.resend.com/emails", headers=headers, json=data)
        if resp.status_code == 200:
            print("[EMAIL] Relatorio enviado com sucesso!")
            return True
        else:
            print(f"[EMAIL] Erro: {resp.status_code} - {resp.text}")
            return False
    except Exception as e:
        print(f"[EMAIL] Erro ao enviar: {e}")
        return False
