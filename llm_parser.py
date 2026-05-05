import json
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

SYSTEM_PROMPT = """Você é um especialista em analisar sites de programas acadêmicos na China.
Sua tarefa é extrair TODAS as informações sobre inscrições abertas, fechadas ou em breve.

Analise o conteúdo fornecido e retorne APENAS um JSON válido com esta estrutura:
{
  "programs": [
    {
      "program_name": "nome do programa",
      "type": "intercambio" | "mestrado" | "pos-graduacao" | "summer-school" | "phd" | "outro",
      "status": "aberta" | "fechada" | "em-breve",
      "open_date": "YYYY-MM-DD" ou null,
      "close_date": "YYYY-MM-DD" ou null,
      "deadline": "YYYY-MM-DD" ou null,
      "url": "link da página de inscrição" ou null,
      "notes": "observações importantes em português" ou null
    }
  ]
}

Regras:
- Extraia TODOS os programas mencionados
- Se não há data específica, use null
- Se não há URL específica, use null
- Se o conteúdo não menciona inscrições, retorne {"programs": []}
- Retorne APENAS o JSON, sem texto adicional
- Datas devem estar no formato YYYY-MM-DD
"""


def parse_with_llm(scraped_data, config):
    llm_config = config["llm"]
    client = OpenAI(
        api_key=os.getenv("OPENROUTER_API_KEY") or llm_config.get("api_key"),
        base_url=llm_config.get("base_url", "https://openrouter.ai/api/v1"),
    )

    all_programs = []

    for site in scraped_data:
        name = site["name"]
        text = site["text"]

        max_chars = llm_config.get("max_tokens", 2000) * 4
        truncated = text[:max_chars]

        prompt = f"""Analise o conteúdo do site "{name}" abaixo e extraia informações sobre inscrições:

---
{truncated}
---

Retorne APENAS o JSON válido."""

        try:
            response = client.chat.completions.create(
                model=llm_config["model"],
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.1,
                max_tokens=llm_config.get("max_tokens", 2000),
            )

            content = response.choices[0].message.content.strip()
            content = content.replace("```json", "").replace("```", "").strip()

            result = json.loads(content)
            programs = result.get("programs", [])

            for p in programs:
                p["source_site"] = name
                p["source_url"] = site["url"]
                all_programs.append(p)

            print(f"  [LLM] {name}: {len(programs)} programa(s) encontrado(s)")

        except json.JSONDecodeError as e:
            print(f"  [LLM ERRO] JSON inválido de {name}: {e}")
            print(f"  Conteúdo: {content[:200]}")
        except Exception as e:
            print(f"  [LLM ERRO] Falha ao processar {name}: {e}")

    return {"programs": all_programs}
