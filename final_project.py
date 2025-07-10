
from dash import dcc, html,Dash

import dash_bootstrap_components as dbc
from dash.dependencies import Output, Input
from dash.exceptions import PreventUpdate
from dash_bootstrap_templates import load_figure_template
import plotly.express as px


import pandas as pd
import numpy as np




resorts = (
    pd.read_csv("/Users/asadali/Downloads/Course_Materials/Data/Ski Resorts/resorts.csv", encoding = "ISO-8859-1")
    .assign(
        country_elevation_rank = lambda x: x.groupby("Country", as_index=False)["Highest point"].rank(ascending=False),
        country_price_rank = lambda x: x.groupby("Country", as_index=False)["Price"].rank(ascending=False),
        country_slope_rank = lambda x: x.groupby("Country", as_index=False)["Total slopes"].rank(ascending=False),
        country_cannon_rank = lambda x: x.groupby("Country", as_index=False)["Snow cannons"].rank(ascending=False),
    ))

dbc_css = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates/dbc.min.css"



Continent_country = {
    "Europe": list(resorts.query("Continent == 'Europe'").loc[:,'Country'].unique()),
    "North America": list(resorts.query("Continent == 'North America'").loc[:,'Country'].unique()),
    "Oceania": list(resorts.query("Continent == 'Oceania'").loc[:,'Country'].unique()),
    "South America":list(resorts.query("Continent == 'South America'").loc[:,'Country'].unique()),
    "Asia":list(resorts.query("Continent == 'Asia'").loc[:,'Country'].unique())
}


app = Dash(__name__, external_stylesheets=[dbc.themes.QUARTZ, dbc_css])
load_figure_template("QUARTZ")

app.layout = dbc.Container(
    dbc.Row([
        dbc.Col([
            dcc.Tabs(id="tabs",className="dbc",children=[
                dcc.Tab(
                    label='Resort Map',
                    value="Resort Map",
                    children=[
                        html.H1(id="tab1-title-output",children="",
                                className="text-center"),
                        dbc.Row([
                            dbc.Col([
                                dbc.Card(
                                    dbc.CardBody([
                                     html.H6("Price limit", className="card-title"),
                                     dcc.Slider(0, 150,
                                     value=30,
                                     id='my-slider'
                                      ),
                                     html.H6(children="Feature Preference",className="mt-2"),
                                     dcc.Checklist(
                                         id='map-checklist',
                                         options=['Has Summer Skiing','Has Night Skiing','Has Snow Park'],
                                         inputStyle={'marginLeft':'2px'}

                                     ),
                                     ])
                                )
                            ],width=3),
                           dbc.Col([
                                dbc.Card(
                                     dbc.CardBody([
                                     dcc.Graph(id='map_graph',figure={}),
                                     ])
                                )
                            ],width=8)

                        ],justify="center")
                    ]
                ),
                dcc.Tab(
                    label='Country Profiler',
                    value="tab2",
                    children=[
                        html.H1(id="second-tab-title", children="",
                                className="text-center"),
                        dbc.Row([
                            dbc.Col([
                                dbc.Card(
                                    dbc.CardBody([
                                    html.P(children="Select the Continent"),
                                    dcc.Dropdown(
                                        id="continent dropdown",
                                        options= list(resorts.loc[:,'Continent'].unique()),
                                        value='Europe',
                                        className="dbc"
                                    ),
                                    html.P(children="Select the Country" ,className="mt-3"),
                                    dcc.Dropdown(id="country-dropdown",value='Norway',className='dbc'),
                                    html.P(children="Select the Metric to plot", className="mt-3"),
                                    dcc.Dropdown(
                                        id="column_int_select",
                                        options =list(resorts.drop('ID',axis=1).select_dtypes(include='int')),
                                        value='Price',
                                        className='dbc'
                                    )

                                    ])
                                  )


                            ],width=3),
                            dbc.Col([
                                dbc.Card(
                                    dbc.CardBody([
                                    dcc.Graph(id='cross_filter',figure={},hoverData={'points': [{'customdata': ['Hemsedal']}]}
                                              ),

                                           ])
                                  )
                            ],width=5),
                            dbc.Col([
                                dbc.Card(
                                    dbc.CardBody([
                                    dbc.Row(
                                        dbc.Col([
                                        dcc.Markdown("### Resort Report Card"),

                                       dbc.Card(id="resort_name",
                                       style={"text-align": "center", "fontSize": 20, "margin-bottom": "20px"},
                                       className="dbc"),

                                    dbc.Row([
                                   dbc.Col([
                                  dbc.Card(id="elevation-kpi", className="dbc", style={"margin-bottom": "10px","padding":"3px","fontSize": "15px"}),
                                dbc.Card(id="price-kpi", className="dbc",style={"margin-bottom": "10px","padding":"5px"})
                               ], className="dbc"),

                          dbc.Col([
                            dbc.Card(id="slope-kpi", className="dbc", style={"margin-bottom": "15px","padding":"3px"}),
                             dbc.Card(id="cannon-kpi", className="dbc",style={"padding":"5px"})
                             ], className="dbc")
                           ])


                                        ])
                                    ),

                                           ])
                                  )


                            ],width=4),
                        ])

                    ]
                )

            ])
        ],width={"size": 10, "offset": 1},className="mt-3")
    ])

)
@app.callback(
    Output("tab1-title-output","children"),
    Output("map_graph","figure"),
    Input("my-slider","value"),
    Input("map-checklist","value")
)
def hello_word(price_value,map_checklist):
    title = f"Resorts with the ticket price  less than ${price_value}"
    df = resorts.query("Price<@price_value")

    if isinstance(map_checklist, list):
        for value in map_checklist:
            if value == 'Has Summer Skiing':
                df = resorts.query("`Summer skiing` == 'Yes'").query("Price<@price_value")
            elif value == 'Has Night Skiing':
                df = resorts.query(" Nightskiing == 'Yes'").query("Price<@price_value")
            elif value == 'Has Snow Park':
                df = resorts.query("Snowparks =='Yes' ").query("Price<@price_value")


    fig = px.density_map(
        df,
        lat='Latitude',
        lon='Longitude',
        z='Total slopes',
        zoom=2,
        center={"lat": 40.0902, "lon": -99.7129},
        radius=25,
        map_style="open-street-map"
    ).update_layout(
        margin={"r":0,"t":20, "l":20,"b":20},
    )



    
    return title,fig


@app.callback(
    Output("country-dropdown","options"),
    Input("continent dropdown","value")
)
def set_continent_options(selected_continent):
    return Continent_country[selected_continent]

@app.callback(
    Output("second-tab-title","children"),
    Output("cross_filter","figure"),
    Input("country-dropdown","value"),
    Input("column_int_select","value")
)
def plot_bar(country, x_bar):
    print(country,'country')
    print(x_bar,'x_bar')
    title = f"Top Resorts in {country} by {x_bar}"
    data =  resorts.query("Country == @country").groupby('Resort',as_index=False).agg({x_bar:'sum'}).sort_values(by=x_bar,ascending=False).iloc[:10]
    fig = px.bar(data, x='Resort', y=x_bar, custom_data=["Resort"])
    fig.update_xaxes(showticklabels=False, ticks="")
    fig.update_layout(
    margin={"r": 20, "t": 20, "l": 20, "b": 20},

    )
    return title,fig


@app.callback(
    Output("resort_name","children"),
           Output("elevation-kpi", "children"),
           Output("price-kpi", "children"),
           Output("slope-kpi", "children"),
           Output("cannon-kpi", "children"),
          Input("cross_filter","hoverData")
)

def report_card(hoverData):
    resort = hoverData["points"][0]["customdata"][0]

    df = resorts.query("Resort == @resort")



    elev_rank = f"Elevation Rank: {int(df['country_elevation_rank'].iloc[0])}"
    price_rank = f"Price Rank: {int(df['country_price_rank'].iloc[0])}"
    slope_rank = f"Slope Rank: {int(df['country_slope_rank'].iloc[0])}"
    cannon_rank = f"Cannon Rank: {int(df['country_cannon_rank'].iloc[0])}"

    return resort, elev_rank, price_rank, slope_rank, cannon_rank




if __name__ == "__main__":
    app.run(debug=True,port=3000)

