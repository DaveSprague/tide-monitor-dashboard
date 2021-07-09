import pathlib
import pandas as pd
import time
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go

APP_PATH = str(pathlib.Path(__file__).parent.resolve())

app = dash.Dash(__name__)
app.scripts.config.serve_locally = True
app.css.config.serve_locally = True
server = app.server
application = app.server

# modify this to match a public key on belfast.pvos.org
feed_a_pubkey = "g3pp988z7ehs"

# base_url = "http://belfast.pvos.org/data/"
#df = pd.read_csv(base_url+feed_a_pubkey+"/csv/")

dfm = pd.read_csv(APP_PATH + '/data/tide_data.csv',
                  index_col='timestamp', parse_dates=True)
# print(dfm.index)
# print(dfm.index.dtype)
# print(dfm.dtypes)

dfm.index = dfm.index.tz_localize('UTC')

START_TIMESTAMP = '2021-6-6 20:16'
START_TIMESTAMP30s = '2021-6-27 0:01'
END_TIMESTAMP = dfm.index[-1]
PREDICTED_END_TIMESTAMP = END_TIMESTAMP + pd.Timedelta(2, unit="d")  # obtain predicted tides two days in the future
END_DATE = END_TIMESTAMP.date().strftime('%Y%m%d')
PREDICTED_END_DATE = PREDICTED_END_TIMESTAMP.date().strftime('%Y%m%d')

est_sensor_height_abv_MLLW_ft = 17.70
dfm["height_ft"] = est_sensor_height_abv_MLLW_ft - dfm['distance_mm'] / 304.8

c0 = dfm.index.to_series().between(START_TIMESTAMP, END_TIMESTAMP)

# create a new dataframe using this index
dfms = dfm[c0]["height_ft"]

print("download predicted tide data")
station = "8415191"  # Belfast, Maine
start_date = "20210606"
end_date = PREDICTED_END_DATE # show predictions for the next two days
timezone = "gmt"
units = "english"
noaa_url = "https://api.tidesandcurrents.noaa.gov/api/prod/datagetter?" + \
    f"begin_date={start_date}" + f"&end_date={end_date}" + f"&station={station}" + "&product=predictions" + \
    "&datum=MLLW" + f"&time_zone={timezone}" + \
    "&interval=hilo" + f"&units={units}" + "&format=csv"
start = time.time()
dfp = pd.read_csv(noaa_url, index_col='Date Time', parse_dates=True)
end = time.time()

colorsIdx = {'H': 'yellow', 'L': 'yellow'}
cols = dfp[' Type'].map(colorsIdx)

print("download took: ", end-start, " seconds")
dfp.index = dfp.index.tz_localize('UTC')

dfmsr6m = dfms.resample('6min').mean()

START_TIMESTAMP30s = '2021-6-27 0:01'
c1 = dfm.index.to_series().between(START_TIMESTAMP30s, PREDICTED_END_TIMESTAMP)
dfms1wk = dfm[c1]["height_ft"]
c2 = dfp.index.to_series().between(START_TIMESTAMP30s, PREDICTED_END_TIMESTAMP)
dfp1wk = dfp[c2]

dfmsr30s = dfms1wk.resample('30s').mean()


colors = {
    'background': '#111111',
    'text': '#7FDBFF'
}

def serve_layout():
    # App Layout
    fig1 = go.Figure()

    fig1.add_trace(go.Scatter(
        x=dfp.index.tz_convert('America/New_York'),
        y=dfp[' Prediction'],
        mode='markers',
        #connectgaps=True,
        name='predictions',
        marker=dict(size=6, opacity=0.5, color=cols),
    ))

    fig1.add_trace(go.Scatter(
        x=dfmsr6m.index.tz_convert('America/New_York'),
        y=dfmsr6m.values,
        mode='lines',
        # connectgaps=True,
        name='measurement',
        line=dict(color='green', width=1),
    ))

    fig1.update_layout(
        title="Predicted vs Measurements 6 Minute Mean Resample",
        plot_bgcolor=colors['background'],
        paper_bgcolor=colors['background'],
        font_color=colors['text'],
    )

    fig2 = go.Figure()

    fig2.add_trace(go.Scatter(
        x=dfp1wk.index.tz_convert('America/New_York'),
        y=dfp1wk[' Prediction'],
        mode='markers',
        #connectgaps=True,
        name='predictions',
        marker=dict(size=6, opacity=0.5, color=cols),
    ))

    fig2.add_trace(go.Scatter(
        x=dfmsr30s.index.tz_convert('America/New_York'),
        y=dfmsr30s.values,
        mode='lines',
        #connectgaps=True,
        name='measurement',
        line=dict(color='green', width=1),
    ))

    fig2.update_layout(
        title="Predicted vs Measurements 30 Second Mean Resample",
        plot_bgcolor=colors['background'],
        paper_bgcolor=colors['background'],
        font_color=colors['text'],
    )

    # fig3 = go.Figure()

    # fig3.add_trace(go.Scatter(
    #     x=dfp.index.tz_convert('America/New_York'),
    #     y=dfp[' Prediction'],
    #     mode='markers',
    #     # connectgaps=True,
    #     name='predictions',
    #     marker=dict(size=6, opacity=0.5, color=cols),
    # ))

    # fig3.add_trace(go.Scatter(
    #     x=dfms.index.tz_convert('America/New_York'),
    #     y=dfms.values,
    #     mode='lines',
    #     # connectgaps=True,
    #     name='measurement',
    #     line=dict(color='darkgreen', width=1),
    # ))

    # fig3.update_layout(
    #     title="Predicted vs Measurements 1 Per Second Samples",
    # )

    return html.Div(
        id="root",
        children=[
            html.Div(
                dcc.Interval(
                    id='interval-component',
                    interval=1*1000,  # in milliseconds
                    n_intervals=0
                )),
            # Main body
            html.Div(
                id="app-container",
                children=[
                    # Banner display
                    html.Div(
                        id="banner",
                        children=[
                            # html.Img(
                            #     id="logo", src=None),
                            html.H2(
                                "Belfast Maine Harbor Tide Dashboard", id="title"),
                        ],
                    ),
                    dcc.Graph(
                        id='6m-graph',
                        figure=fig1
                    ),

                    html.Hr(),

                    dcc.Graph(
                        id='30s-graph',
                        figure=fig2
                    ),

                    # dcc.Graph(
                    #     id='1s-graph',
                    #     figure=fig3
                    # ),



                    html.Div(id='output-image-stats', children=[html.H5("Stats Here")],
                             style={"color": "white"}),

                    html.Div(id='weather-link', children=[dcc.Link('Daily Summary of Weather',
                            href='https://www.weatherlink.com/embeddablePage/show/d41852debc194fc7ae36b72009abb3a7/summary', style={'color':'lightblue'}, target='_blank'),
                            ],
                    ),

                    html.Div(id='iframe-div', children=[
                        html.Iframe(src="https://www.weatherlink.com/embeddablePage/show/77e1eee650594d0387d50b4cfe0fbf6b/signature",
                            height="250", width="760", style={"text-align": "center"}),
                        ],
                    ),


                ],
                style={
                    #"position": "fixed",
                    # "float": "left",
                    #"width": "100%",
                    # "height": "100%",
                    #"overflow": "auto",
                }
            ),

        ],
        # style= {
        #                     "height": "98%",
        #                     "overflow": "hidden",
        #                     "margin": "0",
        #                 }
    )


app.layout = serve_layout

# Running the server
if __name__ == "__main__":
    app.run_server(debug=True, host='127.0.0.1', port=8050)
