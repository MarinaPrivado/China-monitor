import schedule
import time
from datetime import datetime
import json
import os
from scraper import scrape_all
from llm_parser import parse_with_llm
from comparator import load_last_results, save_results, compare_with_last
from email_sender import send_email


def run_check(config, send_email_flag=False):
    print(f"\n{'='*60}")
    print(f"[SCHEDULER] Verificação iniciada: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"{'='*60}")

    scraped = scrape_all(config)
    if not scraped:
        print("[SCHEDULER] Nenhum site acessível. Abortando.")
        return

    results = parse_with_llm(scraped, config)
    last = load_last_results()
    comparison = compare_with_last(results, last)
    save_results(results)

    if send_email_flag and results.get("programs"):
        print("\n[EMAIL] Enviando relatório semanal...")
        send_email(
            config,
            results["programs"],
            comparison["new"],
            comparison["changed"],
            comparison["closed"],
        )

    print(f"\n[SCHEDULER] Verificação completa. {len(results.get('programs', 0))} programa(s) encontrado(s).")


def start_scheduler(config):
    email_day = config.get("schedule", {}).get("email_day", "monday")
    email_time = config.get("schedule", {}).get("email_time", "09:00")

    print("[SCHEDULER] Agendamento configurado:")
    print(f"  Verificação: a cada {config['check_interval_hours']}h")
    print(f"  Email semanal: {email_day} às {email_time}")

    schedule.every(config["check_interval_hours"]).hours.do(
        lambda: run_check(config, send_email_flag=False)
    )

    day_map = {
        "monday": schedule.monday,
        "tuesday": schedule.tuesday,
        "wednesday": schedule.wednesday,
        "thursday": schedule.thursday,
        "friday": schedule.friday,
        "saturday": schedule.saturday,
        "sunday": schedule.sunday,
    }

    scheduler_day = day_map.get(email_day.lower(), schedule.monday)
    scheduler_day.at(email_time).do(lambda: run_check(config, send_email_flag=True))

    print("\n[SCHEDULER] Iniciando. Pressione Ctrl+C para parar.\n")

    run_check(config, send_email_flag=False)

    while True:
        schedule.run_pending()
        time.sleep(60)
