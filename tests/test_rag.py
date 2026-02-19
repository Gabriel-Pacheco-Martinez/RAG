# General
import json
import pytest

# Nodes
from src.nodes.retrieval.rag import use_rag

# Import user message object
from src.models.query import QueryRequest

# Load test cases
with open("tests/tests.json", "r", encoding="utf-8") as f:
    tests = json.load(f)

# Run tests
@pytest.mark.parametrize("case", tests, ids=[case["mensaje"] for case in tests])
def test_rag(case):
    # Define state
    state = {
        "user_message": case["mensaje"],
        "topic": case["topic"]
    }

    # Run rag
    vector = use_rag(state)
    texto_id = vector.payload["texto_id"]
    
    # Evaluate
    result = texto_id == case["texto_id"]
    assert result, f"Message: {case['mensaje']}, esperado: {case['texto_id']}, recibimos: {texto_id}"