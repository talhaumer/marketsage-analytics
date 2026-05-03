import ast
import pathlib

SRC = pathlib.Path(__file__).parent.parent / "src"
ROOT = pathlib.Path(__file__).parent.parent

def _source(rel):
    return (ROOT / rel).read_text(encoding="utf-8")

def test_no_hardcoded_coingecko_key():
    src = _source("src/tools/crypto_data_tools.py")
    assert "CG-" not in src, "Hard-coded CoinGecko API key found in source"

def test_cors_not_wildcard():
    src = _source("src/api/main.py")
    assert 'allow_origins=["*"]' not in src, "CORS wildcard must be removed"

def test_gradio_share_false():
    for path in ["src/frontend/gradio_app.py", "src/frontend/gradio_app_with_viz.py", "run_frontend.py"]:
        src = _source(path)
        assert "share=True" not in src, f"share=True found in {path}"

def test_no_hardcoded_paths():
    src = _source("src/frontend/gradio_app_with_viz.py")
    assert "/Users/talha.umer" not in src, "Hard-coded macOS path found"


def test_no_dead_crypto_agents():
    dead = [
        "src/agents/optimized_crypto_agent.py",
        "src/agents/crypto_data_agent.py",
    ]
    for path in dead:
        assert not (ROOT / path).exists(), f"Dead file still exists: {path}"


def test_no_src_prefix_imports():
    import re
    bad = []
    pattern = re.compile(r"from src\.(tools|agents|workflows|api|utils|frontend)")
    for py in (ROOT / "src").rglob("*.py"):
        for i, line in enumerate(py.read_text(encoding="utf-8").splitlines(), 1):
            if pattern.search(line):
                bad.append(f"{py.relative_to(ROOT)}:{i}: {line.strip()}")
    assert not bad, "Found src-prefixed imports:\n" + "\n".join(bad)
