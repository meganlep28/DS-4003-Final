import pandas as pd
import plotly.express as px
import numpy as np
from dash import Dash, dcc, html, Input, Output, State, callback

###loading JSON file that has the geometry information for US counties

from urllib.request import urlopen
import json
with urlopen('https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json') as response:
    counties = json.load(response)

counties["features"][0]
#sometimes json will run window forcibly closed host error; make a syntax error and reload to fix



#load data
mergedRace = pd.read_csv("FINAL_DATA.csv", header = 0, dtype={"5-digit FIPS Code": str} )


stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css'] # load the CSS stylesheet

app = Dash(__name__, external_stylesheets=stylesheets) # initialize the app

server = app.server

#-----------------------------------APP LAY OUT--------------------------------#
#-----------------------------------APP LAY OUT--------------------------------#
#-----------------------------------APP LAY OUT--------------------------------#

app.layout = html.Div([                     # for everything
    
        html.Div([
        html.H1('Preventable Hospital Stays Analysis', style={'text-align': 'center'}),
        html.H4('What is a preventable hospital stay?', style={'text-align': 'left', 'font-weight': 'bold'}),
        html.P('Hospital stays for ambulatory care sensitive conditions, meaning it could have been treated earlier but was not. Thus, resulting in seeking hospital care (ex. diabetes, heart disease, COPD)'),
        html.P('Instructions: Select options from the dropdown menus to display data. *Note certain options will have less data points*')
        ],  style= {'font-family':'Georgia, serif', 'backgroundColor':'#274442', 'color': '#E9E5E3'}), 


    #for all hist inputs and graphs
    html.Div([

        #for hist inputs only
        html.Div([
            html.Label('Frequency Distribution of Preventable Hospital Stays per County Based on Inputted Values'),
            html.Div(children = [
              html.Label('Food Index Value', style={'font-size': '15px', 'font-weight': 'bold'}), 
              dcc.Dropdown(
                options = mergedRace['Food Environment Index raw value'].unique(),
                value ='7 to 8', #default
                id='drop-food'
              ),
            ]),

            html.Div(children = [
              html.Label('Percent of Diabetes', style={'font-size': '15px', 'font-weight': 'bold'}), 
              dcc.Dropdown(
                options = mergedRace['Diabetes Prevalence raw value'].unique(),
                #options = sorted(mergedRace['Diabetes Prevalence raw value'].dropna().unique(), key=lambda x: x),
                value = '10-15%', #default
                id='drop-diabetes'
              ),
            ]), 

            html.Div(children = [
              html.Label('Median Household Income', style={'font-size': '15px', 'font-weight': 'bold'}), 
              dcc.Dropdown(
                options = mergedRace['Median Household Income raw value'].unique(),
                value = '$50000 - $60000', #default
                id='drop-income'
              ),
            ])
        ], className='four columns', style= {'font-family':'Georgia, serif', 'backgroundColor': '#A3BAB4','color': '#4F7375'}),

        #for hist graph

        html.Div([
        html.Div([
            html.Div([dcc.Graph(id='model-graph')],style= {'font-family':'Georgia, serif', 'color': 'light pink'} )
        ], className ='eight columns'),
        ], className = 'row' )

    ]), #END OF  HIST 

    #CHOROPLETH ALL INPUTS / GRAPHS
    html.Div([

        #for choro inputs
        html.Div([
        html.Label('Distribution of PHS rate by Race and Region', style={'font-size': '15px', 'font-weight': 'bold'}),
        
        html.Div([
            html.Label('Select Region'),
            html.Div([dcc.Dropdown(
                mergedRace['Region'].unique(),
                '', #default
                id='drop_select_region'
            )
        ])
    ]),

        html.Div([
            html.Label('Select Race', style={'font-size': '15px'}),
            html.Div([dcc.Dropdown(
                mergedRace['Race'].unique(),
                '', #default
                id='drop_select_race'
            )
        ])
    ]),
    ],  className='four columns', style= {'font-family':'Georgia, serif', 'backgroundColor': '#A3BAB4','color': '#4F7375'}),   #end choro inputs

        #for choro graphs
        html.Div([
        html.Div([
            html.Div([dcc.Graph(id='region-choro')],style= {'font-family':'Georgia, serif'} )
        ], className ='eight columns'),
        ], className = 'row' )

    ])



] )# for everything




#--------------------------------------HIST CALLBACK-----------------------------------#
#--------------------------------------HIST CALLBACK-----------------------------------#
#--------------------------------------HIST CALLBACK-----------------------------------#

@app.callback(
    Output('model-graph', 'figure'),
    Input('drop-food','value'),
    Input('drop-diabetes', 'value'),
    Input('drop-income', 'value')
) 
def update_model(food_selected, diabetes_selected, income_selected): #need to get all the bins together and then choose a drop down instead of input (bin together certain values, bin together percentage values, bin together income values)

    filteredFood = mergedRace[mergedRace['Food Environment Index raw value'] == food_selected]
    filteredDiabetes = filteredFood[filteredFood['Diabetes Prevalence raw value'] == diabetes_selected]
    filteredIncome = filteredDiabetes[filteredDiabetes['Median Household Income raw value'] == income_selected]


    fig = px.histogram( filteredIncome, x='Preventable Hospital Stay Value', color_discrete_sequence=['lightgreen'],opacity=0.7)
    fig.update_layout(title='Histogram of Predicted Preventable Hospital Stay Value',
                      xaxis_title='Predicted Preventable Hospital Stay Value',
                      yaxis_title='Frequency')

    return fig

    
# # run app
# if __name__ == '__main__':
#     app.run_server(jupyter_mode='tab')

    

#--------------------------------------CHORO CALLBACK-----------------------------------#
#--------------------------------------CHORO CALLBACK-----------------------------------#
#--------------------------------------CHORO CALLBACK-----------------------------------#


@app.callback(
    Output('region-choro', 'figure'),
    Input('drop_select_region', 'value'), 
    Input('drop_select_race', 'value') 
)
def update_output(region_selected, race_selected):

    filtered = mergedRace[mergedRace.Region == region_selected]
    filteredRace = filtered[filtered.Race == race_selected]

    #create fig
    fig = px.choropleth(filteredRace, geojson=counties, locations='5-digit FIPS Code', color='Preventable Hospital Stay Value',
                        color_continuous_scale="Viridis",
                           range_color=(0, 10000),
                           scope="usa",
                           labels={'Preventable Hospital Stay Value':'Avg PHS rate'},
                           title = "Choropleth of PHS rate by Region and Race"
                          )
    return fig

# run the app

if __name__ == '__main__':
    app.run_server(jupyter_mode='tab')


