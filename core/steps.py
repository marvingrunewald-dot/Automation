from dataclasses import dataclass, asdict
from typing import Any, Dict, Type

@dataclass
class BaseStep:
    type: str

@dataclass
class ClickStep(BaseStep):
    screenshot: str
    elapsed: float = 0.0
    ocr_enabled: bool = False
    ocr_text: str = ""

    def __init__(self, screenshot: str, elapsed: float = 0.0,
                 ocr_enabled: bool = False, ocr_text: str = ""):
        super().__init__("click")
        self.screenshot = screenshot
        self.elapsed = elapsed
        self.ocr_enabled = ocr_enabled
        self.ocr_text = ocr_text

@dataclass
class TextStep(BaseStep):
    text: str

    def __init__(self, text: str):
        super().__init__("text")
        self.text = text

@dataclass
class KeyStep(BaseStep):
    key: str

    def __init__(self, key: str):
        super().__init__("key")
        self.key = key

@dataclass
class WaitStep(BaseStep):
    duration: float

    def __init__(self, duration: float):
        super().__init__("wait")
        self.duration = duration

# Platzhalter für Vision-Schritte (kannst du später erweitern)
@dataclass
class VisionClickStep(BaseStep):
    search_text: str

    def __init__(self, search_text: str):
        super().__init__("vision_click")
        self.search_text = search_text

@dataclass
class VisionCheckStep(BaseStep):
    search_text: str
    must_exist: bool = True

    def __init__(self, search_text: str, must_exist: bool = True):
        super().__init__("vision_check")
        self.search_text = search_text
        self.must_exist = must_exist

STEP_CLASSES: Dict[str, Type[BaseStep]] = {
    "click": ClickStep,
    "text": TextStep,
    "key": KeyStep,
    "wait": WaitStep,
    "vision_click": VisionClickStep,
    "vision_check": VisionCheckStep,
}

def step_to_dict(step: BaseStep) -> Dict[str, Any]:
    return asdict(step)

def step_from_dict(data: Dict[str, Any]) -> BaseStep:
    t = data.get("type")
    cls = STEP_CLASSES.get(t)
    if not cls:
        raise ValueError(f"Unbekannter Schritt-Typ: {t}")

    if cls is ClickStep:
        return ClickStep(
            screenshot=data["screenshot"],
            elapsed=data.get("elapsed", 0.0),
            ocr_enabled=data.get("ocr_enabled", False),
            ocr_text=data.get("ocr_text", ""),
        )
    if cls is TextStep:
        return TextStep(text=data.get("text", ""))
    if cls is KeyStep:
        return KeyStep(key=data.get("key", ""))
    if cls is WaitStep:
        return WaitStep(duration=data.get("duration", 0.0))
    if cls is VisionClickStep:
        return VisionClickStep(search_text=data.get("search_text", ""))
    if cls is VisionCheckStep:
        return VisionCheckStep(
            search_text=data.get("search_text", ""),
            must_exist=data.get("must_exist", True),
        )

    raise ValueError(f"Fehlende Implementierung für Typ: {t}")
