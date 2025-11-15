import json
from typing import List

from core.steps import BaseStep, step_to_dict, step_from_dict

def save_project(path: str, steps: List[BaseStep]):
    data = [step_to_dict(s) for s in steps]
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

def load_project(path: str) -> List[BaseStep]:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return [step_from_dict(d) for d in data]
