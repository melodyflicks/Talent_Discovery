from ai.skills.normalizer import normalize_skill


def test_skill_normalization():
    assert normalize_skill(" Python ") == "Python"
    assert normalize_skill(" Python ").lower() == "python"
