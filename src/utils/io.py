import json
from config.settings import PROMPTS_PATH

def read_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
    
def write_json(data, path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def load_prompt(file: str) -> str:
    with open(PROMPTS_PATH + file, "r", encoding="utf-8") as f:
        return f.read()