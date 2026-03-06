# General
import json
import pytest

# Nodes
from src.nodes.generate.rag import llm_rag_retrieval

# Import user message object
from src.models.query import QueryRequest

# Load test cases
with open("tests/textos.json", "r", encoding="utf-8") as f:
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
    vectors = llm_rag_retrieval(state)

    # Collect returned texto_ids
    ids = [vector.payload["texto_id"] for vector in vectors]

    # Expected value(s)
    expected = case["texto_id"]

    if isinstance(expected, list):
        # True if ANY returned id is in expected list
        result = any(i in expected for i in ids)
    else:
        # True if expected id is inside returned ids
        result = expected in ids

    assert result, (
        f"Message: {case['mensaje']}, "
        f"esperado: {expected}, "
        f"recibimos: {ids}"
    )