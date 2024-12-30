# Import required libraries
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Define launch_sites
launch_sites = spacex_df['Launch Site'].unique()

#Create options for the dropdown
options = [{'label': 'All Sites', 'value': 'ALL'}] + [{'label': site, 'value': site} for site in launch_sites]

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                html.Div(dcc.Dropdown(id='site-dropdown',
                                                      options=options,
                                                      value='ALL',
                                                      placeholder="Select a Launch Site",
                                                      searchable=True)),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),

                                # TASK 3: Add a slider to select payload range
                                dcc.RangeSlider(id='payload-slider',
                                                min=0, max=10000, step=1000,
                                                marks={i: f'{i} kg' for i in range (0, 10001, 1000)},
                                                value=[min_payload, max_payload]),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(Output(component_id='success-pie-chart', component_property='figure'),
              Input(component_id='site-dropdown', component_property='value'))

def get_pie_chart(entered_site):
    if entered_site == 'ALL':
        # Count successes per site
        success_counts = spacex_df[spacex_df['class']==1].groupby('Launch Site').size().reset_index(name='Successes')
        fig = px.pie(data_frame=success_counts,
                     values='Successes',
                     names = 'Launch Site',
                     title = 'Total Success Launches by Site')
        return fig
    else:
        # Filter data for the selected site
        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]
        success_counts = filtered_df['class'].value_counts().reset_index(name='Counts')
        success_counts.columns = ['class', 'Counts']
        fig = px.pie(data_frame=success_counts,
                     values='Counts',
                     names='class',
                     title=f'Success and Failure Counts for site {entered_site}')
        return fig

# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(Output(component_id='success-payload-scatter-chart', component_property='figure'),
              [Input(component_id='site-dropdown', component_property='value'), Input(component_id='payload-slider', component_property='value')])

def update_scatter_plot(entered_site, payload_range):
    # Extracting the min and max payload from the slider's value
    min_payload, max_payload = payload_range

    # Filtering the dataframe based on the selected site and payload range
    if entered_site == 'ALL':
        # No site filter, just payload range filter
        filtered_df = spacex_df[(spacex_df['Payload Mass (kg)'] >= min_payload) &
                                (spacex_df['Payload Mass (kg)'] <= max_payload)]
        title = 'Payload Mass vs Launch Outcome (All Sites)'
    else:
        # Filter the dataframe based on the selected site and payload range
        filtered_df = spacex_df[(spacex_df['Launch Site'] == entered_site) &
                                (spacex_df['Payload Mass (kg)'] >= min_payload) &
                                (spacex_df['Payload Mass (kg)'] <= max_payload)]
        title = f'Payload Mass vs Launch Outcome ({entered_site})'

    # Create a scatter plot with Payload Mass on x-axis and class on y-axis
    fig = px.scatter(data_frame=filtered_df,
                     x='Payload Mass (kg)',
                     y='class',
                     color='Booster Version Category',
                     title=title,
                     labels={'class': 'Launch Outcome (0: Fail, 1: Success)', 'Payload Mass (kg)': 'Payload Mass (kg)'})

    return fig

# Run the app
if __name__ == '__main__':
    app.run_server()
