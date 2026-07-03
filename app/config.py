# ============================================================================
# Personalized Networking Assistant — Application Configuration
# ============================================================================
# Centralized settings for the entire backend. Uses Pydantic BaseSettings
# for environment-variable support and type-safe defaults.
# ============================================================================

from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application-wide configuration.

    Every field can be overridden by setting an environment variable with the
    same name (case-insensitive). For example:
        export APP_HOST=0.0.0.0
        export WIKIPEDIA_BASE_URL=https://...
    """

    # ── Server ──────────────────────────────────────────────────────────────
    app_name: str = "Personalized Networking Assistant"
    app_version: str = "1.0.0"
    app_host: str = "127.0.0.1"
    app_port: int = 8000
    debug: bool = False

    # ── AI / NLP Model Identifiers ──────────────────────────────────────────
    classifier_model: str = "typeform/distilbert-base-uncased-mnli"
    generator_model: str = "gpt2"

    # ── External APIs ───────────────────────────────────────────────────────
    wikipedia_base_url: str = "https://en.wikipedia.org/api/rest_v1/page/summary/"
    wikipedia_timeout: int = 10  # seconds

    # ── Data Storage Paths ──────────────────────────────────────────────────
    # Paths are resolved relative to the project root at runtime.
    data_dir: str = "data"
    history_file: str = "history.json"
    feedback_file: str = "feedback.json"

    # ── Zero-Shot Classification Labels ─────────────────────────────────────
    # Default candidate labels used by the event analyzer when the caller
    # does not supply custom labels.
    default_candidate_labels: list[str] = [
        "Artificial Intelligence",
        "Machine Learning",
        "Data Science",
        "Sustainability",
        "Climate Change",
        "Healthcare",
        "Finance",
        "Education",
        "Technology",
        "Blockchain",
        "Cybersecurity",
        "Robotics",
        "Urban Planning",
        "Renewable Energy",
        "Biotechnology",
        "Cloud Computing",
        "Entrepreneurship",
        "Social Impact",
        "Digital Transformation",
        "Supply Chain",
    ]

    class Config:
        env_prefix = ""  # allow bare env-var names

    # ── Derived helpers ─────────────────────────────────────────────────────

    def get_data_dir(self) -> Path:
        """Return an absolute Path to the data directory, creating it if needed."""
        path = Path(self.data_dir).resolve()
        path.mkdir(parents=True, exist_ok=True)
        return path

    def get_history_path(self) -> Path:
        """Full path to the conversation-history JSON file."""
        return self.get_data_dir() / self.history_file

    def get_feedback_path(self) -> Path:
        """Full path to the user-feedback JSON file."""
        return self.get_data_dir() / self.feedback_file


# ---------------------------------------------------------------------------
# Singleton instance — import this throughout the application.
# ---------------------------------------------------------------------------
settings = Settings()
