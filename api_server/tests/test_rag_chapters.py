# General
import json
import pytest

# Nodes
from src.nodes.llm.rag import use_rag

# Import user message object
from src.models.query import QueryRequest

# Load test cases
with open("tests/capitulos2.json", "r", encoding="utf-8") as f:
    tests = json.load(f)

# Run tests
@pytest.mark.parametrize("case", tests, ids=[case["mensaje"] for case in tests])
def test_rag(case):
    # Define state
    state = {
        "user_message": case["mensaje"],
        "topic": case["topic"]
    }

    # Run rag chapg
    chapter_id = use_rag(state)
    
    # Evaluate
    expected = case["chapter_id"]

    if isinstance(expected, list):
        result = chapter_id in expected
    else:
        result = chapter_id == expected
    assert result, f"Message: {case['mensaje']}, esperado: {case['chapter_id']}, recibimos: {chapter_id}"