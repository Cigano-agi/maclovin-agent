import json
import urllib.parse
from maclovin.config import load_config
from maclovin.core.pipeline import Pipeline
from maclovin.intelligence.factory import create_llm_provider
from maclovin.ingestion.category_classifier import classify_category


def app(environ, start_response):
    try:
        cfg = load_config()
        provider = create_llm_provider(cfg.ai)
        pipeline = Pipeline(config=cfg, llm_provider=provider, db_connection=None)
        report = pipeline.run(dry_run=True)

        tools = [it.model_dump(mode="json") for it in report.tools_and_launches]
        business = [it.model_dump(mode="json") for it in report.business_items]
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

        # Garantir re-classificação estrita
        all_items = tools + business + news + learning + geek
        final_tools = []
        final_business = []
        final_news = []
        final_learning = []
        final_geek = []

        for item in all_items:
            cat = classify_category(item.get("title", ""), item.get("summary", ""), item.get("item_type", "news"))
            item["item_type"] = "tool" if cat == "tools" else cat
            if cat == "tools":
                final_tools.append(item)
            elif cat == "business":
                final_business.append(item)
            elif cat == "learning":
                final_learning.append(item)
            elif cat == "geek":
                final_geek.append(item)
            else:
                final_news.append(item)

        payload = {
            "status": "SUCCESS",
            "date": report.reference_date.isoformat(),
            "total_items": len(final_tools) + len(final_business) + len(final_news) + len(final_learning) + len(final_geek),
            "tools": final_tools,
            "business": final_business,
            "news": final_news,
            "learning": final_learning,
            "geek": final_geek,
            "latest_execution": {
                "reference_date": report.reference_date.isoformat(),
                "status": "SUCCESS",
                "items_collected_count": len(final_tools) + len(final_business) + len(final_news) + len(final_learning) + len(final_geek),
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
