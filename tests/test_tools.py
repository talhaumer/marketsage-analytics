import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent / "src"))


def test_prefetch_returns_shared_market_data_key():
    from workflows.data_prefetch import prefetch_market_data
    state = {"symbols": [], "timeframe": "1mo", "analysis_type": "quick",
             "question": "test", "risk_tolerance": "moderate"}
    result = prefetch_market_data(state)
    assert "shared_market_data" in result
    assert isinstance(result["shared_market_data"], dict)


def test_prefetch_handles_empty_symbols():
    from workflows.data_prefetch import prefetch_market_data
    result = prefetch_market_data({"symbols": [], "timeframe": "1mo",
             "analysis_type": "quick", "question": "test", "risk_tolerance": "moderate"})
    assert result["shared_market_data"] == {}


def test_tool_invoke_uses_dict_not_positional():
    import ast
    bad_calls = []
    for path in pathlib.Path("src/tools").glob("*.py"):
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if (isinstance(node, ast.Call)
                    and isinstance(node.func, ast.Attribute)
                    and node.func.attr == "invoke"
                    and len(node.args) > 1):
                bad_calls.append(f"{path.name}:{node.lineno}")
    assert not bad_calls, f"Wrong .invoke() positional calls: {bad_calls}"
