import json
import yaml
from config.settings import SCHEMAS_PATH
from config.settings import PROMPTS_PATH

def read_json(path) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
    
def write_json(data, path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def load_prompt(file: str) -> str:
    with open(PROMPTS_PATH +file, "r", encoding="utf-8") as f:
        return f.read()

def load_json_schema(file: str) -> dict:
    with open(SCHEMAS_PATH + file, "r", encoding="utf-8") as f:
        return json.load(f)
    
def load_yaml_schema(file:str) -> dict:
    with open(SCHEMAS_PATH + file, "r") as f:
        return yaml.safe_load(f)
