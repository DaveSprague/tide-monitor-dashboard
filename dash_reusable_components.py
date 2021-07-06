

import dash_core_components as dcc
import dash_html_components as html

import plotly.graph_objs as go

# Display utility functions
def _merge(a, b):
    return dict(a, **b)


def _omit(omitted_keys, d):
    return {k: v for k, v in d.items() if k not in omitted_keys}





# Custom Display Components
def Card(children, **kwargs):
    return html.Section(
        children,
        style=_merge(
            {
                "padding": 20,
                "margin": 5,
                # Remove possibility to select the text for better UX
                "user-select": "none",
                "-moz-user-select": "none",
                "-webkit-user-select": "none",
                "-ms-user-select": "none",
            },
            kwargs.get("style", {}),
        ),
        **_omit(["style"], kwargs),
    )


def NamedSlider(name, id, min, max, step, value, marks=None):
    if marks:
        step = None
    else:
        marks = {i: i for i in range(min, max + 1, step)}

    return html.Div(
        style={"margin": "25px 5px 30px 0px"},
        children=[
            f"{name}:",
            html.Div(
                style={"margin-left": "5px"},
                children=dcc.Slider(
                    id=id, min=min, max=max, marks=marks, step=step, value=value
                ),
            ),
        ],
    )


def NamedInlineRadioItems(name, short, options, val, **kwargs):
    return html.Div(
        id=f"div-{short}",
        style=_merge(
            {"display": "block", "margin-bottom": "5px", "margin-top": "5px"},
            kwargs.get("style", {}),
        ),
        children=[
            f"{name}:",
            dcc.RadioItems(
                id=f"radio-{short}",
                options=options,
                value=val,
                labelStyle={
                    "display": "inline-block",
                    "margin-right": "7px",
                    "font-weight": 300,
                },
                style={"display": "inline-block", "margin-left": "7px"},
            ),
        ],
        **_omit(["style"], kwargs),
    )





def CustomDropdown(**kwargs):
    return html.Div(
        dcc.Dropdown(**kwargs), style={"margin-top": "5px", "margin-bottom": "5px"}
    )
