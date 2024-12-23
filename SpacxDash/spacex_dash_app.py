# Import required libraries
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the spacex data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Prepare launch sites options for the dropdown
launch_sites = [{'label': site, 'value': site} for site in spacex_df['Launch Site'].unique()]
launch_sites.insert(0, {'label': 'All Sites', 'value': 'All Sites'})  # Add 'All Sites' option

# Create an app layout
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard', style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}),
    
    # Dropdown for Launch Site selection
    dcc.Dropdown(
        id='site-dropdown',
        options=launch_sites,
        value='All Sites',
        placeholder="Select a Launch Site here",
        searchable=True
    ),
    html.Br(),
    
    # Pie chart for showing successful launches
    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),
    
    html.P("Payload range (Kg):"),
    
    # Slider for selecting payload range
    dcc.RangeSlider(
        id='payload-slider',
        min=0,
        max=10000,
        step=1000,
        value=[min_payload, max_payload],
        marks={2500: {'label': '2500 (Kg)'}, 5000: {'label': '5000 (Kg)'}, 7500: {'label': '7500 (Kg)'}}
    ),
    
    # Scatter chart for showing payload vs. success
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])

# Callback for the success-pie-chart (TASK 2)
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
)
def select(inputt):
    if inputt == 'All Sites':
        # Grouping by 'Launch Site' and summing the success (class)
        new_df = spacex_df.groupby(['Launch Site'])["class"].sum().to_frame().reset_index()
        fig = px.pie(new_df, values='class', names='Launch Site', title='Total Success Launches by Site')
    else:
        # Filtering by the selected site and counting the success/failure
        new_df = spacex_df[spacex_df["Launch Site"] == inputt]["class"].value_counts().reset_index()
        new_df.columns = ['name', 'class']  # Renaming columns to match expected format
        new_df = new_df.set_index('name')  # Setting 'name' column as the index
        
        # Ensure that both 'Success' and 'Failure' are present in the data, even if one is missing
        new_df = new_df.reindex(['Failure', 'Success'], fill_value=0)
        
        fig = px.pie(new_df, values='class', names=new_df.index, title=f'Total Success Launches for {inputt}')
    
    return fig

# Callback for the success-payload-scatter-chart (TASK 4)
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value'),
    Input(component_id='payload-slider', component_property='value')
)
def scatter(input1, input2):
    print(input1)
    print(input2)
    
    # Filter based on Launch Site and Payload Range
    if input1 == 'All Sites':
        new_df = spacex_df
    else:
        new_df = spacex_df[spacex_df["Launch Site"] == input1]
    
    # Filter by payload range
    new_df = new_df[(new_df["Payload Mass (kg)"] >= input2[0]) & (new_df["Payload Mass (kg)"] <= input2[1])]
    
    # Scatter plot: Payload Mass vs. Launch Success
    fig2 = px.scatter(
        new_df,
        y="class",
        x="Payload Mass (kg)",
        color="Booster Version Category",
        title=f"Launch Success vs. Payload Mass for {input1} (Payload Range: {input2[0]} - {input2[1]})"
    )
    
    return fig2

# Run the Dash app
if __name__ == '__main__':
    app.run_server(debug=True, port=8051)