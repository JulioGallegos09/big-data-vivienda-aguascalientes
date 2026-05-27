from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_RAW = ROOT / "data" / "raw"
DATA_PROCESSED = ROOT / "data" / "processed"
MODELS = ROOT / "models"
RESULTS = ROOT / "results"
FIGURES = RESULTS / "figures"
DOCS = ROOT / "docs"


def ensure_dirs() -> None:
    for path in (DATA_RAW, DATA_PROCESSED, MODELS, RESULTS, FIGURES, DOCS):
        path.mkdir(parents=True, exist_ok=True)
