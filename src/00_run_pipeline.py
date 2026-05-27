import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = [
    "01_collect_data.py",
    "02_clean_features.py",
    "03_train_models.py",
    "04_evaluate.py",
    "05_validate_outputs.py",
]


def main() -> None:
    for script in SCRIPTS:
        script_path = ROOT / "src" / script
        print(f"\n==> Ejecutando {script}")
        subprocess.run([sys.executable, str(script_path)], check=True)


if __name__ == "__main__":
    main()
