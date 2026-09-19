import pytest
from ai.resume.preprocessing import prepare_document
def test_resume_boundary_is_explicit():
    with pytest.raises(NotImplementedError): prepare_document("sample.pdf")
