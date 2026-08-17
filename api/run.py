import json
import urllib.parse
from maclovin.config import load_config
from maclovin.core.pipeline import Pipeline
from maclovin.intelligence.factory import create_llm_provider


def app(environ, start_response):
    try:
        cfg = load_config()
        provider = create_llm_provider(cfg.ai)
        pipeline = Pipeline(config=cfg, llm_provider=provider, db_connection=None)
        report = pipeline.run(dry_run=True)

        tools = [it.model_dump(mode="json") for it in report.tools_and_launches]
        news = [it.model_dump(mode="json") for it in report.standalone_news] + [
            {
                "id": ev.id,
                "source_id": ev.main_topic_id,
                "title": ev.title,
                "canonical_url": ev.news_items[0].canonical_url if ev.news_items else "#",
                "published_date_utc": f"{report.reference_date.isoformat()}T12:00:00Z",
                "summary": ev.consolidated_summary,
                "why_it_matters": ev.why_it_matters,
                "pricing_model": "Não especificado",
                "item_type": "news",
                "key_features": [],
            }
            for ev in report.events
        ]
        learning = [it.model_dump(mode="json") for it in report.learning_items]
        geek = [it.model_dump(mode="json") for it in report.geek_items]

        payload = {
            "status": "SUCCESS",
            "date": report.reference_date.isoformat(),
            "total_items": len(tools) + len(news) + len(learning) + len(geek),
            "tools": tools,
            "news": news,
            "learning": learning,
            "geek": geek,
            "latest_execution": {
                "reference_date": report.reference_date.isoformat(),
                "status": "SUCCESS",
                "items_collected_count": len(tools) + len(news) + len(learning) + len(geek),
            },
        }

        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        status = "200 OK"
        headers = [
            ("Content-Type", "application/json; charset=utf-8"),
            ("Access-Control-Allow-Origin", "*"),
            ("Content-Length", str(len(body))),
        ]
        start_response(status, headers)
        return [body]

    except Exception as e:
        error_payload = json.dumps({"status": "ERROR", "message": str(e)}).encode("utf-8")
        status = "500 Internal Server Error"
        headers = [
            ("Content-Type", "application/json; charset=utf-8"),
            ("Access-Control-Allow-Origin", "*"),
            ("Content-Length", str(len(error_payload))),
        ]
        start_response(status, headers)
        return [error_payload]
