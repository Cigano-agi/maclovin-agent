"""Parser to extract structured briefing payload from Markdown reports."""

import pathlib
import re
from typing import Dict, Any, List
from maclovin.intelligence.translator import translate_to_pt_br
from maclovin.ingestion.category_classifier import classify_category, classify_tool_subtype


def extract_briefing_from_markdown(file_path: pathlib.Path) -> Dict[str, Any]:
    """Extrai itens e categorias estruturadas a partir de um arquivo Markdown salvo."""
    content = file_path.read_text(encoding="utf-8")
    ref_date = file_path.stem

    tools: List[Dict[str, Any]] = []
    opportunities: List[Dict[str, Any]] = []
    business: List[Dict[str, Any]] = []
    news: List[Dict[str, Any]] = []
    learning: List[Dict[str, Any]] = []
    geek: List[Dict[str, Any]] = []

    current_section = None
    lines = content.splitlines()

    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if "## 🛠️ Radar de Ferramentas" in line:
            current_section = "tools"
        elif "## 💡 Oportunidades" in line:
            current_section = "opportunities"
        elif "## 💼 Business" in line:
            current_section = "business"
        elif "## 📚 Aprender Tecnologia" in line:
            current_section = "learning"
        elif "## 🎮 Universo Geek" in line:
            current_section = "geek"
        elif "## 📰 Principais Notícias" in line:
            current_section = "news"
        elif line.startswith("## 📊"):
            current_section = None

        if current_section and line.startswith("### "):
            title = re.sub(r"^### \d+\.\s*", "", line)
            source_id = "feed"
            pricing = "Não especificado"
            summary = ""
            why = ""
            url = "#"

            j = i + 1
            features = []
            while j < len(lines) and not lines[j].strip().startswith("### ") and not lines[j].strip().startswith("## "):
                sub = lines[j].strip()
                if "**Fonte:**" in sub:
                    src_match = re.search(r"\*\*Fonte:\*\*\s*`([^`]+)`", sub)
                    if src_match:
                        source_id = src_match.group(1)
                    if "[GRÁTIS" in sub:
                        pricing = "Grátis / Open-Source"
                    elif "[FREEMIUM]" in sub:
                        pricing = "Freemium"
                    elif "[PAGO" in sub:
                        pricing = "Pago"
                elif sub.startswith("> **O que faz:**") or sub.startswith(">"):
                    summary = sub.replace("> **O que faz:**", "").replace(">", "").strip()
                elif "💡" in sub or "💰" in sub:
                    why = re.sub(r"^[💡💰]\s*(\*\*[^:]+:\*\*)?\s*", "", sub)
                elif sub.startswith("- ✔"):
                    features.append(sub.replace("- ✔", "").strip())
                elif "🔗 **Link" in sub:
                    url_match = re.search(r"\[([^\]]+)\]\(([^)]+)\)", sub)
                    if url_match:
                        url = url_match.group(2)
                j += 1

            translated_title = translate_to_pt_br(title)
            translated_summary = translate_to_pt_br(summary or title)
            translated_why = translate_to_pt_br(why) if why else "Acompanhamento relevante para inovação e desenvolvimento."

            real_cat = classify_category(translated_title, translated_summary, current_section)
            subtype = classify_tool_subtype(translated_title, translated_summary, url) if real_cat == "tools" else "app"

            item = {
                "id": f"{real_cat}-{len(tools)+len(opportunities)+len(business)+len(news)+len(learning)+len(geek)+1}",
                "source_id": source_id,
                "title": translated_title,
                "canonical_url": url,
                "published_date_utc": f"{ref_date}T12:00:00Z",
                "summary": translated_summary,
                "why_it_matters": translated_why,
                "pricing_model": pricing,
                "item_type": "tool" if real_cat == "tools" else real_cat,
                "tool_subtype": subtype,
                "key_features": [translate_to_pt_br(f) for f in features],
            }

            if real_cat == "tools":
                tools.append(item)
            elif real_cat == "opportunities":
                opportunities.append(item)
            elif real_cat == "business":
                business.append(item)
            elif real_cat == "learning":
                learning.append(item)
            elif real_cat == "geek":
                geek.append(item)
            else:
                news.append(item)

        i += 1

    return {
        "date": ref_date,
        "total_items": len(tools) + len(opportunities) + len(business) + len(news) + len(learning) + len(geek),
        "tools": tools,
        "opportunities": opportunities,
        "business": business,
        "learning": learning,
        "geek": geek,
        "news": news,
        "latest_execution": {
            "reference_date": ref_date,
            "status": "SUCCESS",
            "items_collected_count": len(tools) + len(opportunities) + len(business) + len(news) + len(learning) + len(geek),
        },
    }
