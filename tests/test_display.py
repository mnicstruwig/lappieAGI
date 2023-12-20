from lappie import display


def test_display(mock_world):  # noqa
    expected_result = """\

    """
    print(mock_world.model_dump_json())
    display.print_world(mock_world)
