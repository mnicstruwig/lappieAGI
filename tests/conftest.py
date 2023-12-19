import pytest
from lappie.models import World, SubQuestion


@pytest.fixture
def mock_world() -> World:
    subquestion_1 = SubQuestion(
        question="Who are the peers of TSLA?",
        answer="Ford, GM, Ferrari"
    )
    subquestion_2 = SubQuestion(
        question="What is the market cap of TSLA's peers?",
        answer="Ford: 10, GM: 20, Ferrari: 30",
        subquestions=[
            SubQuestion(
                question="What is the market cap of Ford?",
                answer= "10"
            ),
            SubQuestion(
                question="What is the market cap of GM?",
                answer= "20"
            ),
            SubQuestion(
                question="What is the market cap of Ferrari?",
            ),
        ]
    )

    return World(
        question="Who are the peers of TSLA? Who is their market cap?",
        answer="Ford: 10, GM: 20, Ferrari: 30",
        subquestions=[subquestion_1, subquestion_2]
    )
