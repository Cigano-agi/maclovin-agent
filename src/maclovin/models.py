"""Domain entities and Pydantic models for maclovin."""

from datetime import datetime, date
from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field, model_validator
import hashlib

PricingModel = Literal["Grátis / Open-Source", "Freemium", "Pago", "Não especificado"]
ItemType = Literal["news", "tool", "learning", "geek", "business", "opportunities"]


class TopicConfig(BaseModel):
    id: str
    name: str
    keywords: List[str] = Field(default_factory=list)
    active: bool = True
    priority: int = Field(default=1, ge=1, le=5)


class SourceConfig(BaseModel):
    id: str
    name: str
    ingestion_type: str = "rss"  # "rss", "atom", "api", "html"
    url: str
    active: bool = True
    timeout_seconds: int = Field(default=10, ge=1, le=60)
    category: str = "news"  # "news", "tools", "learning", "geek", "business", "opportunities"


class SettingsConfig(BaseModel):
    timezone: str = "America/Sao_Paulo"
    output_dir: str = "briefings"
    database_path: str = "data/maclovin.db"
    log_level: str = "INFO"
    web_port: int = 8000


class AIConfig(BaseModel):
    provider: str = "gemini"  # "gemini", "openai", "nvidia", "anthropic", "ollama", "glm"
    model: str = "gemini-2.5-flash"
    base_url: Optional[str] = None  # Ex: "https://integrate.api.nvidia.com/v1"
    api_key_env_var: Optional[str] = None  # Ex: "NVIDIA_API_KEY" ou "OPENAI_API_KEY"
    temperature: float = Field(default=0.1, ge=0.0, le=1.0)
    timeout_seconds: int = Field(default=30, ge=5, le=120)


class AppConfig(BaseModel):
    version: str = "1.0"
    settings: SettingsConfig = Field(default_factory=SettingsConfig)
    ai: AIConfig = Field(default_factory=AIConfig)
    topics: List[TopicConfig] = Field(default_factory=list)
    sources: List[SourceConfig] = Field(default_factory=list)


class NewsItem(BaseModel):
    id: str
    source_id: str
    title: str
    canonical_url: str
    published_date_utc: datetime
    collected_date_utc: datetime = Field(default_factory=datetime.utcnow)
    raw_content: Optional[str] = None
    content_hash: str = ""
    topic_ids: List[str] = Field(default_factory=list)
    relevance_score: float = 0.0
    item_type: str = "news"  # "news", "tool", "learning", "geek", "business", "opportunities"
    tool_subtype: str = "app"  # "repo" (repositório GitHub/open-source) ou "app" (software/SaaS)
    pricing_model: str = "Não especificado"  # "Grátis / Open-Source", "Freemium", "Pago", "Não especificado"
    key_features: List[str] = Field(default_factory=list)
    summary: Optional[str] = None
    why_it_matters: Optional[str] = None
    thumbnail_url: Optional[str] = None

    @model_validator(mode="after")
    def compute_content_hash_and_id(self) -> "NewsItem":
        if not self.content_hash:
            payload = (self.title + (self.raw_content or "")).encode("utf-8")
            self.content_hash = hashlib.sha256(payload).hexdigest()
        if not self.id:
            self.id = hashlib.sha256(self.canonical_url.encode("utf-8")).hexdigest()[:16]
        return self


class EventCluster(BaseModel):
    id: str
    reference_date: date
    title: str
    main_topic_id: str
    news_items: List[NewsItem] = Field(default_factory=list)
    news_item_ids: List[str] = Field(default_factory=list)
    relevance_score: float = 0.0
    consolidated_summary: str
    why_it_matters: Optional[str] = None


class BriefingReport(BaseModel):
    id: str  # YYYY-MM-DD
    reference_date: date
    generated_at_utc: datetime = Field(default_factory=datetime.utcnow)
    events: List[EventCluster] = Field(default_factory=list)
    tools_and_launches: List[NewsItem] = Field(default_factory=list)
    business_items: List[NewsItem] = Field(default_factory=list)
    opportunity_items: List[NewsItem] = Field(default_factory=list)
    learning_items: List[NewsItem] = Field(default_factory=list)
    geek_items: List[NewsItem] = Field(default_factory=list)
    standalone_news: List[NewsItem] = Field(default_factory=list)
    execution_stats: Dict[str, Any] = Field(default_factory=dict)
    alerts: List[str] = Field(default_factory=list)


class ExecutionRecord(BaseModel):
    id: str
    reference_date: str
    started_at_utc: datetime
    finished_at_utc: Optional[datetime] = None
    status: str  # "SUCCESS", "PARTIAL_FAILURE", "FAILED"
    sources_queried_count: int = 0
    sources_failed_count: int = 0
    items_collected_count: int = 0
    duplicates_ignored_count: int = 0
    errors_json: Optional[str] = None


# AI Structured Response schemas
class ClassificationResult(BaseModel):
    is_relevant: bool
    topic_ids: List[str] = Field(default_factory=list)
    relevance_score: float = Field(default=0.0, ge=0.0, le=1.0)
    item_type: str = "news"  # "news", "tool", "learning", "geek"
    pricing_model: str = "Não especificado"
    key_features: List[str] = Field(default_factory=list)


class SummaryResult(BaseModel):
    title: str
    summary: str
    why_it_matters: Optional[str] = None
    item_type: str = "news"
    pricing_model: str = "Não especificado"
    key_features: List[str] = Field(default_factory=list)
    insufficient_data: bool = False


class EventClusterResult(BaseModel):
    event_title: str
    main_topic_id: str
    relevance_score: float = Field(default=0.0, ge=0.0, le=1.0)
    consolidated_summary: str
    why_it_matters: Optional[str] = None
