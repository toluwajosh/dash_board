"""
Create a results dashboard with dash
"""

import argparse
import json
from pathlib import Path
from typing import List

import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
from dash.dependencies import Input, Output
from pprint import pprint

external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
colors = {"background": "#111111", "text": "#85c1e9", "accent": "#eb984e"}


def get_data() -> List:
    """Callback function to get results from directory

    Returns:
        [List]: A list of results object
    """
    results_dir = Path("./examples/results")
    all_results = [x for x in results_dir.iterdir() if x.suffix == ".json"]
    all_data = []
    for data_path in all_results:
        with open(str(data_path)) as json_file:
            all_data.append(json.load(json_file))
            # all_data += json.load(json_file)
    return all_data


def combine_metrics(all_data):
    all_metrics = {}
    for sub_data in all_data:
        for metric in sub_data["metrics"]:
            if metric["metric"] not in all_metrics:
                # create new data
                all_metrics[metric["metric"]] = [
                    {
                        "method": sub_data["method"],
                        "results": metric["results"],
                        "summary": metric["summary"],
                    }
                ]
            else:
                # update old
                all_metrics[metric["metric"]].append(
                    {
                        "method": sub_data["method"],
                        "results": metric["results"],
                        "summary": metric["summary"],
                    }
                )
    return all_metrics


app.layout = html.Div(
    id="all-results",
    style={"backgroundColor": colors["background"]},
    children=[
        html.H1(
            children="Results Dashboard",
            style={"textAlign": "center", "color": colors["text"]},
        ),
        html.Div(
            children="Quick visualization of experiment results.",
            style={"textAlign": "center", "color": colors["accent"]},
        ),
        html.Div(id="results-div"),
        html.Div(id="summaries-div"),
        # to retrieve results automatically at intervals
        dcc.Interval(
            id="interval-component", interval=5 * 1000, n_intervals=0  # in milliseconds
        ),
    ],
)


@app.callback(
    Output("results-div", "children"), [Input("interval-component", "n_intervals")]
)
def update_results_div(value):
    all_data = combine_metrics(get_data())
    return [
        dcc.Graph(
            id="results-graph",
            figure={
                "layout": {
                    "title": metric,  # data["metric"] # this should be metric name
                    "plot_bgcolor": colors["background"],
                    "paper_bgcolor": colors["background"],
                    "font": {"color": colors["text"]},
                },
                "data": [
                    {
                        "x": [x["category"] for x in data["results"]],
                        "y": [y["score"] for y in data["results"]],
                        "type": "bar",
                        "name": data["method"],  # sub_data["method"], data["metric"]
                    }
                    for data in sub_data
                ],
            },
        )
        for (metric, sub_data) in all_data.items()
    ]


@app.callback(
    Output("summaries-div", "children"), [Input("interval-component", "n_intervals")]
)
def update_summaries_div(value):
    all_data = combine_metrics(get_data())
    return [
        dcc.Graph(
            id="summaries-graph",
            figure={
                "layout": {
                    "title": "Summary: " + metric,
                    "plot_bgcolor": colors["background"],
                    "paper_bgcolor": colors["background"],
                    "font": {"color": colors["text"]},
                },
                "data": [
                    {
                        "x": list(data["summary"].keys()),
                        "y": list(data["summary"].values()),
                        "type": "bar",
                        "name": data["method"],
                    }
                    for data in sub_data
                ],
            },
        )
        for (metric, sub_data) in all_data.items()
    ]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run Dashboard Server",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,  # type: ignore
    )
    parser.add_argument("--host", type=str, default="127.0.0.1", help="Host address.")
    parser.add_argument("--port", type=str, default="5555", help="Port Number.")
    args = parser.parse_args()
    app.run_server(debug=True, host=args.host, port=args.port)
