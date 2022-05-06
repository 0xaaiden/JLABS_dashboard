import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import numpy as np
from dash.dependencies import Output, Input
from generate_graph import *


data["Timestamp"] = pd.to_datetime(data["Timestamp"])
figdefault = generate_fig("5x", 100000,data.Timestamp.min(), data.Timestamp.max())

external_stylesheets = [
    {
        "href": "https://fonts.googleapis.com/css2?"
        "family=Lato:wght@400;700&display=swap",
        "rel": "stylesheet",
    },
]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server
app.title = "Jarvis Labs Analytics"

app.layout = html.Div(
    children=[
        html.Div(
            children=[
                html.P(children=[
                    html.Img(src="/assets/logo.png", className="header-logo")
                ], className="header-emoji"),
                html.H1(
                    children="Jarvis Labs Dashboard", className="header-title"
                )
                # html.P(
                #     children="Analyze the behavior of avocado prices"
                #     " and the number of avocados sold in the US"
                #     " between 2015 and 2018",
                #     className="header-description",
                # ),
            ],
            className="header",
        ),
        html.Div(
            children=[
                html.Div(
                    children=[
                        html.Div(children="Liquidation Level", className="menu-title"),
                        dcc.Dropdown(
                            id="liq-filter",
                            options=[
                                {"label": liqlevel, "value": liqlevel}
                                for liqlevel in liq_levels.keys()
                            ],
                            value="5x",
                            clearable=False,
                            className="dropdown",
                        ),
                    ]
                ),
                html.Div(
                    children=[
                        html.Div(children="Trade Filters", className="menu-title"),
                        dcc.Dropdown(
                            id="trade-filter",
                            options=[
                                {"label": "> ${:,.0f}".format(trade_size), "value": trade_size}
                                for trade_size in trade_sizes
                            ],
                            value=100000,
                            clearable=False,
                            searchable=False,
                            className="dropdown",
                        ),
                    ],
                ),
                html.Div(
                    children=[
                        html.Div(
                            children="Date Range",
                            className="menu-title"
                            ),
                        dcc.DatePickerRange(
                            id="date-range",
                            min_date_allowed=data.Timestamp.min().date(),
                            max_date_allowed=data.Timestamp.max().date(),
                            start_date=data.Timestamp.min().date(),
                            end_date= data.Timestamp.max().date(),
                            updatemode= "bothdates"
                        ),
                    ]
                ),
            ],
            className="menu",
        ),
        html.Div(
            children=[
                dcc.Loading(children=[html.Div(
                    children=dcc.Graph(
                        id="price-chart", animate=True, figure=figdefault, config={"displayModeBar": True}
                    ),
                    className="card",
                )],
                            
                            style={"box-shadow": "0 4px 6px 0 rgb(0 0 0 / 18%)", "margin-bottom": "24px"}
                            )
                
            ],
            className="wrapper",
        ),
    ]
)


app.layout = html.Div(
    children=[
        html.Div(
            children=[
                html.P(children=[
                    html.Img(src="/assets/logo.png", className="header-logo")
                ], className="header-emoji"),
                html.H1(
                    children="Jarvis Labs Dashboard", className="header-title"
                )
                # html.P(
                #     children="Analyze the behavior of avocado prices"
                #     " and the number of avocados sold in the US"
                #     " between 2015 and 2018",
                #     className="header-description",
                # ),
            ],
            className="header",
        ),
        html.Div(
            children=[
                html.Div(
                    children=[
                        html.Div(children="Liquidation Level", className="menu-title"),
                        dcc.Dropdown(
                            id="liq-filter",
                            options=[
                                {"label": liqlevel, "value": liqlevel}
                                for liqlevel in liq_levels.keys()
                            ],
                            value="5x",
                            clearable=False,
                            className="dropdown",
                        ),
                    ]
                ),
                html.Div(
                    children=[
                        html.Div(children="Trade Filters", className="menu-title"),
                        dcc.Dropdown(
                            id="trade-filter",
                            options=[
                                {"label": "> ${:,.0f}".format(trade_size), "value": trade_size}
                                for trade_size in trade_sizes
                            ],
                            value=100000,
                            clearable=False,
                            searchable=False,
                            className="dropdown",
                        ),
                    ],
                ),
                html.Div(
                    children=[
                        html.Div(
                            children="Date Range",
                            className="menu-title"
                            ),
                        dcc.DatePickerRange(
                            id="date-range",
                            min_date_allowed=data.Timestamp.min().date(),
                            max_date_allowed=data.Timestamp.max().date(),
                            start_date=data.Timestamp.min().date(),
                            end_date= data.Timestamp.max().date(),
                            updatemode= "bothdates"
                        ),
                    ]
                ),
            ],
            className="menu",
        ),
        html.Div(
            children=[
                dcc.Loading(children=[html.Div(
                    children=dcc.Graph(
                        id="price-chart", figure=figdefault, config={"displayModeBar": 'hover', "displaylogo": False, "editable": True}
                    ),
                    className="card",
                )],
                            type="dot",
                            style={ "margin-bottom": "24px"}
                            )
                
            ],
            className="wrapper",
        ),
    ]
)


@app.callback(
    Output("price-chart", "figure"),
    [
        Input("liq-filter", "value"),
        Input("trade-filter", "value"),
        Input("date-range", "start_date"),
        Input("date-range", "end_date"),
    ],prevent_initial_call=True
)
def update_charts(liq_level, trade_size, start_date, end_date):

    print(liq_level, trade_size, start_date, end_date)
    try:
        fig2 = generate_fig(liq_level, trade_size, start_date, end_date)
        print("figure generated")
        return fig2
    except:
        print("exception happening")
        return figdefault


    
if __name__ == "__main__":
    app.run_server(debug=False)

