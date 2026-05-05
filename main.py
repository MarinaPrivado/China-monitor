import json
import sys
import os
from dotenv import load_dotenv

load_dotenv()

def load_config():
    config_path = os.path.join(os.path.dirname(__file__), "config.json")
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def main():
    config = load_config()

    if len(sys.argv) > 1 and sys.argv[1] == "--once":
        from scraper import scrape_all
        from llm_parser import parse_with_llm
        from comparator import load_last_results, save_results, compare_with_last
        from email_sender import send_email

        send_email_flag = "--email" in sys.argv

        scraped = scrape_all(config)
        if not scraped:
            print("Nenhum site acessível.")
            sys.exit(1)

        results = parse_with_llm(scraped, config)
        last = load_last_results()
        comparison = compare_with_last(results, last)
        save_results(results)

        if send_email_flag:
            send_email(config, results["programs"], comparison["new"], comparison["changed"], comparison["closed"])

        print(f"\n{'='*60}")
        print(f"Encontrados {len(results.get('programs', []))} programa(s)")
        for p in results.get("programs", []):
            status_icon = "🟢" if p["status"] == "aberta" else "🔴" if p["status"] == "fechada" else "🟡"
            print(f"  {status_icon} {p['program_name']} ({p['type']}) - {p['status']}")
            if p.get("deadline"):
                print(f"     Prazo: {p['deadline']}")
    else:
        from scheduler import start_scheduler
        start_scheduler(config)


if __name__ == "__main__":
    main()
