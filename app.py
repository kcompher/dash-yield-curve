# -*- coding: utf-8 -*-
# Import required libraries
import os
import pandas as pd
import numpy as np

import plotly.plotly as py
from plotly.graph_objs import *

import flask
import dash
from dash.dependencies import Input, Output, State, Event
import dash_core_components as dcc
import dash_html_components as html


# Setup the app
server = flask.Flask(__name__)
server.secret_key = os.environ.get('secret_key', 'secret')
app = dash.Dash(__name__, server=server, url_base_pathname='/dash/gallery/yield-curve/', csrf_protect=False)

app.css.append_css({
    'external_url': (
        'https://cdn.rawgit.com/chriddyp/0247653a7c52feb4c48437e1c1837f75'
        '/raw/a68333b876edaf62df2efa7bac0e9b3613258851/dash.css'
    )
})

if 'DYNO' in os.environ:
    app.scripts.append_script({
        'external_url': 'https://cdn.rawgit.com/chriddyp/ca0d8f02a1659981a0ea7f013a378bbd/raw/e79f3f789517deec58f41251f7dbb6bee72c44ab/plotly_ga.js'  # noqa: E501
    })

app.layout = html.Div([
    html.Div(
        [
            dcc.Markdown(
                '''
                ### A View of a Chart That Predicts The Economic Future: The Yield Curve
                This interactive report is a rendition of a
                [New York Times original](https://www.nytimes.com/interactive/2015/03/19/upshot/3d-yield-curve-economic-growth.html).
                '''.replace('  ', ''),
                className='eight columns offset-by-two'
            )
        ],
        className='row',
        style={'text-align': 'center', 'margin-bottom': '30px'}
    ),
    html.Div(
        [
            html.Div(
                [
                    dcc.Slider(
                        min=0,
                        max=5,
                        value=0,
                        marks={i: ''.format(i+1) for i in range(6)},
                        id='slider'
                    ),
                ],
                className='row',
                style={'margin-bottom': '20px'}
            ),
            html.Div(
                [
                    html.Div(
                        [
                            # html.Button('Back', id='back'),
                            html.Button('Next', id='next')
                        ],
                        className='one column offset-by-three'
                    ),
                    dcc.Markdown(
                        id='text',
                        className='six columns'
                    ),
                ],
                className='row'
            ),
            dcc.Graph(
                id='graph',
                style={'height': '60vh'}
            ),
        ],
        id='page'
    ),
])


# Internal logic

global slider_position
slider_position = 0

df = pd.read_csv("data/yield_curve.csv")

xlist = list(df["x"].dropna())
ylist = list(df["y"].dropna())

del df["x"]
del df["y"]

zlist = []
for row in df.iterrows():
    index, data = row
    zlist.append(data.tolist())

UPS = {
    0: dict(x=0, y=0, z=1),
    1: dict(x=0, y=0, z=1),
    2: dict(x=0, y=0, z=1),
    3: dict(x=0, y=0, z=1),
    4: dict(x=0, y=0, z=1),
    5: dict(x=0, y=0, z=1),
}

CENTERS = {
    0: dict(x=-0.2, y=0.2, z=-0.5),
    1: dict(x=0, y=0, z=-0.37),
    2: dict(x=0, y=1.1, z=-1.3),
    3: dict(x=0, y=-0.7, z=0),
    4: dict(x=0, y=-0.2, z=0),
    5: dict(x=-0.11, y=-0.5, z=0),
}

EYES = {
    0: dict(x=2.7, y=2.7, z=0.5),
    1: dict(x=0.01, y=3.3, z=-0.37),
    2: dict(x=1.3, y=3, z=0),
    3: dict(x=2.6, y=-1.6, z=0),
    4: dict(x=3, y=-0.2, z=0),
    5: dict(x=-0.1, y=-0.5, z=2.66)
}

TEXTS = {
    0: '''
    #### Yield curve 101
    The yield curve shows how much it costs the federal government to borrow
    money for a given amount of time, revealing the relationship between long-
    and short-term interest rates.
    >>
    It is, inherently, a forecast for what the economy holds in the future —
    how much inflation there will be, for example, and how healthy growth will
    be over the years ahead — all embodied in the price of money today,
    tomorrow and many years from now.
    '''.replace('  ', ''),
    1: '''
    #### Where we stand
    On Wednesday, both short-term and long-term rates were lower than they have
    been for most of history – a reflection of the continuing hangover
    from the financial crisis.
    >>
    The yield curve is fairly flat, which is a sign that investors expect
    mediocre growth in the years ahead.
    '''.replace('  ', ''),
    2: '''
    #### Deep in the valley
    In response to the last recession, the Federal Reserve has kept short-term
    rates very low — near zero — since 2008. (Lower interest rates stimulate
    the economy, by making it cheaper for people to borrow money, but also
    spark inflation.)
    >>
    Now, the Fed is getting ready to raise rates again, possibly as early as
    June.
    '''.replace('  ', ''),
    3: '''
    #### Last time, a puzzle
    The last time the Fed started raising rates was in 2004. From 2004 to 2006,
    short-term rates rose steadily.
    >>
    But long-term rates didn't rise very much.
    >>
    The Federal Reserve chairman called this phenomenon a “conundrum," and it
    raised questions about the ability of the Fed to guide the economy.
    Part of the reason long-term rates failed to rise was because of strong
    foreign demand.
    '''.replace('  ', ''),
    4: '''
    #### Long-term rates are low now, too
    Foreign buyers have helped keep long-term rates low recently, too — as have
    new rules encouraging banks to hold government debt and expectations that
    economic growth could be weak for a long time.
    >>
    The 10-year Treasury yield was as low as it has ever been in July 2012 and
    has risen only modestly since.
    Some economists refer to the economic pessimism as “the new normal.”
    '''.replace('  ', ''),
    5: '''
    #### Long-term rates are low now, too
    Here is the same chart viewed from above.
    '''.replace('  ', '')
}


# Make 3d graph
@app.callback(Output('graph', 'figure'), [Input('slider', 'value')])
def make_graph(value):

    trace = dict(
        type="surface",
        x=xlist,
        y=ylist,
        z=zlist,
        lighting={
            "ambient": 0.95,
            "diffuse": 0.99,
            "fresnel": 0.01,
            "roughness": 0.01,
            "specular": 0.01,
        },
        colorscale=[[0, "#E6F5FE"], [0.4, "#7BABCB"], [0.8, "#2877AE"], [1, "#253D51"]],
        showscale=False,
        zmax=9.18,
        zmin=0,
        scene="scene",
    )

    layout = dict(
        # width=1650,
        # height=900,
        autosize=True,
        font=dict(
            size=12,
            color="#CCCCCC",
        ),
        margin=dict(
            t=5,
            l=5,
            b=5,
            r=5,
        ),
        showlegend=False,
        hovermode="closest",
        scene=dict(
            aspectmode="manual",
            aspectratio=dict(x=2, y=5, z=1.5),

            camera=dict(
                up=UPS[value],
                center=CENTERS[value],
                eye=EYES[value]
            ),
            xaxis={
                "showgrid": True,
                "title": "",
                "type": "category",
                "zeroline": False,
                "categoryorder": 'array',
                "categoryarray": list(reversed(xlist))
            },
            yaxis={
                "showgrid": True,
                "title": "",
                "type": "date",
                "zeroline": False,
            },
        )
    )

    data = [trace]
    figure = dict(data=data, layout=layout)

    return figure


# Make annotations
@app.callback(Output('text', 'children'), [Input('slider', 'value')])
def make_text(value):
    return TEXTS[value]


# Button controls
@app.callback(Output('slider', 'value'),
              state=[State('slider', 'value')],
              events=[Event('next', 'click')])
def advance_slider(slider):
    if slider < 5:
        slider += 1

    return slider


# Run the Dash app
if __name__ == '__main__':
    app.server.run(debug=True, threaded=True)
