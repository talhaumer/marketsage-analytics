import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent / "src"))

import pytest


def test_basic_chart_returns_figure():
    import plotly.graph_objects as go
    fig = go.Figure(go.Scatter(x=[1, 2, 3], y=[4, 5, 6]))
    assert isinstance(fig, go.Figure)
    assert len(fig.data) == 1


def test_empty_figure_has_no_data():
    import plotly.graph_objects as go
    fig = go.Figure()
    assert len(fig.data) == 0


def test_chart_layout_title():
    import plotly.graph_objects as go
    fig = go.Figure()
    fig.update_layout(title="Test Chart", xaxis_title="Date")
    assert fig.layout.title.text == "Test Chart"
