# AI Provider Interface Contract

**Feature**: `001-daily-news-agent`  
**Pattern**: Strategy / Adapter Interface  

## 1. Interface Base (`BaseLLMProvider`)

```python
from abc import ABC, abstractmethod
from pydantic import BaseModel
from typing import List, Optional

class ClassificationResult(BaseModel):
    is_relevant: bool
    topic_ids: List[str]
    relevance_score: float  # 0.0 a 1.0

class SummaryResult(BaseModel):
    title: str
    summary: str
    why_it_matters: Optional[str] = None
    insufficient_data: bool = False

class EventClusterResult(BaseModel):
    event_title: str
    main_topic_id: str
    relevance_score: float
    consolidated_summary: str
    why_it_matters: str

class BaseLLMProvider(ABC):
    @abstractmethod
    def classify_news(self, title: str, text: str, topics: list) -> ClassificationResult:
        """Classifica se a matéria é relevante para os tópicos do usuário."""
        pass

    @abstractmethod
    def summarize_news(self, title: str, text: str, topic_context: str) -> SummaryResult:
        """Gera resumo factual estrito (Strict Grounding) e justificativa 'Por que importa'."""
        pass

    @abstractmethod
    def cluster_events(self, items: list) -> List[EventClusterResult]:
        """Agrupa múltiplas notícias sobre o mesmo acontecimento em um único EventCluster."""
        pass
```
