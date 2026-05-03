import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent / "src"))

from workflows.state import string_reducer, dict_reducer, error_reducer, list_reducer

def test_string_reducer_returns_new_when_provided():
    assert string_reducer("old", "new") == "new"

def test_string_reducer_returns_existing_when_new_is_none():
    assert string_reducer("old", None) == "old"

def test_dict_reducer_merges():
    assert dict_reducer({"a": 1}, {"b": 2}) == {"a": 1, "b": 2}

def test_dict_reducer_new_wins_on_conflict():
    assert dict_reducer({"a": 1}, {"a": 99}) == {"a": 99}

def test_error_reducer_concatenates():
    assert error_reducer("err1", "err2") == "err1; err2"

def test_error_reducer_handles_none():
    assert error_reducer(None, "err2") == "err2"
    assert error_reducer("err1", None) == "err1"

def test_list_reducer_last_write_wins():
    assert list_reducer(["a"], ["b", "c"]) == ["b", "c"]

def test_list_reducer_keeps_existing_when_new_is_none():
    assert list_reducer(["a"], None) == ["a"]

def test_list_reducer_returns_empty_list_for_none_existing():
    assert list_reducer(None, None) == []
