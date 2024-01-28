from lappie.tree import find_subquestion, delete_subquestion_2


def test_find_subquestion_second_level(mock_world):
    target_question_id = mock_world.subquestions[1].subquestions[1].id

    expected_result = mock_world.subquestions[1].subquestions[1]
    actual_result = find_subquestion(mock_world, question_id=target_question_id)

    assert actual_result == expected_result


def test_find_subquestion_first_level(mock_world):
    target_question_id = mock_world.subquestions[1].id

    expected_result = mock_world.subquestions[1]
    actual_result = find_subquestion(mock_world, question_id=target_question_id)

    assert actual_result == expected_result


def test_find_subquestion_top_level(mock_world):
    target_question_id = mock_world.id

    expected_result = mock_world
    actual_result = find_subquestion(mock_world, question_id=target_question_id)

    assert actual_result == expected_result


def test_find_subquestion_after_nested(mock_world_2):
    mock_world = mock_world_2
    target_question_id = mock_world.subquestions[-1].id

    expected_result = mock_world_2.subquestions[-1]
    actual_result = find_subquestion(mock_world, question_id=target_question_id)

    assert actual_result == expected_result


def test_find_subquestion_doesnt_exist(mock_world_2):
    mock_world = mock_world_2
    target_question_id = "not in table"

    expected_result = None
    actual_result = find_subquestion(mock_world, question_id=target_question_id)

    assert actual_result == expected_result

def test_delete_subquestion(mock_world):
    target_question_id = mock_world.subquestions[0].id

    breakpoint()
    delete_subquestion_2(mock_world, target_question_id)
    breakpoint()
