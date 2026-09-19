from .parser import parse_resume
def extract(text: str) -> dict: return parse_resume(text)
