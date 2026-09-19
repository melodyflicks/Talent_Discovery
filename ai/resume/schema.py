from dataclasses import dataclass, field

@dataclass
class ExtractedResume:
    text: str
    candidates: dict[str, list[str]] = field(default_factory=dict)
