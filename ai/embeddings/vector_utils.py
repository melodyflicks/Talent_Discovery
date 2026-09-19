def cosine_similarity(left: list[float], right: list[float]) -> float:
    if len(left) != len(right) or not left: raise ValueError("Vectors must be non-empty and equally sized")
    numerator = sum(a * b for a, b in zip(left, right))
    left_norm = sum(a * a for a in left) ** 0.5
    right_norm = sum(b * b for b in right) ** 0.5
    return numerator / (left_norm * right_norm) if left_norm and right_norm else 0.0
