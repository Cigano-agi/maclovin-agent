"""Abstract base class for LLM providers."""

from abc import ABC, abstractmethod
from typing import List
from maclovin.models import (
    ClassificationResult,
    SummaryResult,
    EventClusterResult,
    TopicConfig,
    NewsItem,
)


class BaseLLMProvider(ABC):
    """Interface abstrata para adaptadores de Inteligência Artificial."""

    @abstractmethod
    def classify_news(
        self,
        title: str,
        text: str,
        topics: List[TopicConfig],
    ) -> ClassificationResult:
        """Avalia a relevância semântica da notícia frente aos tópicos monitorados."""
        pass

    @abstractmethod
    def summarize_news(
        self,
        title: str,
        text: str,
        topic_context: str,
    ) -> SummaryResult:
        """Gera resumo conciso fundamentado estritamente no texto fornecido (Anti-Alucinação)."""
        pass

    @abstractmethod
    def cluster_events(
        self,
        items: List[NewsItem],
    ) -> List[EventClusterResult]:
        """Agrupa matérias e republicações sobre o mesmo acontecimento em eventos consolidados."""
        pass
