import yaml
from pathlib import Path

def load_config(name="model_config.yaml"):
    path = Path(__file__).parent / name
    with open(path) as f:
        return yaml.safe_load(f)