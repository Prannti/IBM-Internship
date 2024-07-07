# -*- coding: utf-8 -*-
"""Untitled7.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1GNjJn9akOO35foOrZX1UWfMfXlPAJo3a
"""

pip install dash pandas plotly

import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

# Load the updated dataset
file_path = '/content/Simulated-FedEx Dataset-UltraPro_Update.csv'
data = pd.read_csv(file_path)

# Extract numeric part of 'Process_ID' for range slider
data['Process_ID_Numeric'] = data['Process_ID'].str.extract(r'(\d+)').astype(int)

# KPI mapping for stakeholders
stakeholder_kpis = {
    'warehouse_manager': ['Cycle_Time', 'Total_Cost', 'Employee_Productivity', 'Resource_Utilization', 'Damaged_Packages', 'Lost_Packages', 'Employee_Turnover_Rate', 'Training_Hours'],
    'delivery_agent': ['Delivery_Time', 'On_Time_Delivery', 'Fuel_Consumption', 'Customer_Complaints', 'Late_Deliveries'],
    'logistics_manager': data.columns.tolist(),
    'general_manager': data.columns.tolist(),
    'marketing_head': ['Customer_Satisfaction', 'On_Time_Delivery', 'Customer_Complaints'],
    'administration_head': ['Total_Cost', 'Vehicle_Maintenance_Cost', 'Employee_Turnover_Rate', 'Training_Hours']
}

# Define applicable visualization types for each KPI
kpi_visualizations = {
    'Cycle_Time': ['Line Chart', 'Scatter Plot', 'Bar Chart'],
    'Total_Cost': ['Line Chart', 'Bar Chart', 'Pie Chart'],
    'Employee_Productivity': ['Line Chart', 'Scatter Plot'],
    'Resource_Utilization': ['Pie Chart', 'Bar Chart'],
    'Damaged_Packages': ['Bar Chart'],
    'Lost_Packages': ['Bar Chart'],
    'Employee_Turnover_Rate': ['Line Chart', 'Scatter Plot'],
    'Training_Hours': ['Line Chart', 'Bar Chart'],
    'Delivery_Time': ['Line Chart', 'Scatter Plot'],
    'On_Time_Delivery': ['Line Chart', 'Bar Chart'],
    'Fuel_Consumption': ['Line Chart', 'Scatter Plot'],
    'Customer_Complaints': ['Line Chart', 'Bar Chart'],
    'Late_Deliveries': ['Bar Chart'],
    'Customer_Satisfaction': ['Line Chart', 'Pie Chart'],
    'Vehicle_Maintenance_Cost': ['Line Chart', 'Bar Chart']
}

# Initialize the Dash app
app = dash.Dash(__name__)

# Define the CSS styles for the dashboard
app.layout = html.Div([
    html.H1("FedEx KPI Dashboard", style={'textAlign': 'center', 'color': 'white', 'background-color': '#0074D9', 'padding': '20px', 'border': '2px solid black'}),
    dcc.Dropdown(
        id='stakeholder-dropdown',
        options=[
            {'label': 'Warehouse Manager', 'value': 'warehouse_manager'},
            {'label': 'Delivery Agent', 'value': 'delivery_agent'},
            {'label': 'Logistics Manager', 'value': 'logistics_manager'},
            {'label': 'General Manager', 'value': 'general_manager'},
            {'label': 'Marketing Head', 'value': 'marketing_head'},
            {'label': 'Administration Head', 'value': 'administration_head'}
        ],
        value='warehouse_manager',
        style={'width': '50%', 'margin': 'auto'}
    ),
    html.Br(),
    html.Label("Select Process ID Range:"),
    dcc.RangeSlider(
        id='process-id-slider',
        min=data['Process_ID_Numeric'].min(),
        max=data['Process_ID_Numeric'].max(),
        value=[data['Process_ID_Numeric'].min(), data['Process_ID_Numeric'].max()],
        marks={i: str(i) for i in range(data['Process_ID_Numeric'].min(), data['Process_ID_Numeric'].max() + 1, 50)},  # Increased interval to 50
        step=1,
        allowCross=False
    ),
    dcc.Tabs(id='kpi-tabs'),
    html.Br(),
    dcc.Dropdown(id='visualization-dropdown', style={'width': '50%', 'margin': 'auto'}),
    html.Div(id='graphs-container', style={'margin-top': '20px', 'border': '2px solid black', 'padding': '10px', 'background-color': '#f0f0f0'}),
    html.Div(id='details-container', style={'margin-top': '20px', 'border': '2px solid black', 'padding': '10px', 'background-color': '#f0f0f0', 'display': 'none'}),
])

# Callback to update KPI tabs based on selected stakeholder
@app.callback(
    Output('kpi-tabs', 'children'),
    [Input('stakeholder-dropdown', 'value')]
)
def update_kpi_tabs(stakeholder):
    kpis = stakeholder_kpis.get(stakeholder, [])
    return [dcc.Tab(label=kpi.replace('_', ' '), value=kpi) for kpi in kpis]

# Callback to update visualization dropdown based on selected KPI
@app.callback(
    Output('visualization-dropdown', 'options'),
    [Input('kpi-tabs', 'value')]
)
def update_visualization_options(selected_kpi):
    if selected_kpi:
        visualizations = kpi_visualizations.get(selected_kpi, [])
        return [{'label': viz, 'value': viz} for viz in visualizations]
    return []

# Callback to update graphs and suggestions based on dropdown selection and range slider
@app.callback(
    [Output('graphs-container', 'children'),
     Output('details-container', 'children'),
     Output('details-container', 'style')],
    [Input('stakeholder-dropdown', 'value'),
     Input('process-id-slider', 'value'),
     Input('kpi-tabs', 'value'),
     Input('visualization-dropdown', 'value')]
)
def update_graphs_and_suggestions(stakeholder, process_id_range, selected_kpi, selected_visualization):
    # Debug print statements
    print(f"Stakeholder: {stakeholder}")
    print(f"Process ID Range: {process_id_range}")
    print(f"Selected KPI: {selected_kpi}")
    print(f"Selected Visualization: {selected_visualization}")

    try:
        # Filter data for selected range
        filtered_data = data[(data['Process_ID_Numeric'] >= process_id_range[0]) & (data['Process_ID_Numeric'] <= process_id_range[1])]

        # Filter data for 'Before' BPR implementation
        filtered_data_before = filtered_data[filtered_data['BPR_Implementation'] == 'Before']

        # Filter data for 'After' BPR implementation
        filtered_data_after = filtered_data[filtered_data['BPR_Implementation'] == 'After']

        if not selected_kpi or not selected_visualization:
            return [], [], {'display': 'none'}

        if selected_visualization == 'Line Chart':
            fig_before = px.line(filtered_data_before, x='Process_ID', y=selected_kpi, title=f'{selected_kpi.replace("_", " ")} - Before')
            fig_after = px.line(filtered_data_after, x='Process_ID', y=selected_kpi, title=f'{selected_kpi.replace("_", " ")} - After')
        elif selected_visualization == 'Scatter Plot':
            fig_before = px.scatter(filtered_data_before, x='Process_ID', y=selected_kpi, title=f'{selected_kpi.replace("_", " ")} - Before')
            fig_after = px.scatter(filtered_data_after, x='Process_ID', y=selected_kpi, title=f'{selected_kpi.replace("_", " ")} - After')
        elif selected_visualization == 'Bar Chart':
            fig_before = px.bar(filtered_data_before, x='Process_ID', y=selected_kpi, title=f'{selected_kpi.replace("_", " ")} - Before')
            fig_after = px.bar(filtered_data_after, x='Process_ID', y=selected_kpi, title=f'{selected_kpi.replace("_", " ")} - After')
        elif selected_visualization == 'Pie Chart' and selected_kpi in ['Resource_Utilization', 'Total_Cost', 'Customer_Satisfaction']:
            fig_before = px.pie(filtered_data_before, names='Process_ID', values=selected_kpi, title=f'{selected_kpi.replace("_", " ")} - Before')
            fig_after = px.pie(filtered_data_after, names='Process_ID', values=selected_kpi, title=f'{selected_kpi.replace("_", " ")} - After')
        else:
            fig_before = None
            fig_after = None

        graphs = []
        if fig_before and fig_after:
            graphs = [
                dcc.Graph(figure=fig_before),
                dcc.Graph(figure=fig_after)
            ]

        # Detailed view logic
        detailed_view = html.Div([
            html.H3(f'Detailed Analysis of {selected_kpi.replace("_", " ").title()}'),
            dcc.Graph(figure=fig_before),
            dcc.Graph(figure=fig_after),
            html.H4('Suggestions:'),
            bpr_analysis(filtered_data_before, stakeholder)
        ])

        # Show details container if a tab is selected
        details_style = {'margin-top': '20px', 'border': '2px solid black', 'padding': '10px', 'background-color': '#f0f0f0'}
        if selected_kpi:
            details_style['display'] = 'block'
        else:
          details_style['display'] = 'none'

        return graphs, detailed_view, details_style

    except Exception as e:
        print(f"Error: {e}")
        return [], [], {'display': 'none'}

# BPR analysis function
def bpr_analysis(filtered_data, stakeholder):
    suggestions = []
    try:
        if stakeholder == 'warehouse_manager':
            if filtered_data['Cycle_Time'].mean() > 5:
                suggestions.append("Consider optimizing the warehouse layout to reduce cycle time.")
            if filtered_data['Total_Cost'].sum() > 100000:
                suggestions.append("Review the procurement process to identify cost-saving opportunities.")
            if filtered_data['Employee_Productivity'].mean() < 10:
                suggestions.append("Implement training programs to boost employee productivity.")
        elif stakeholder == 'delivery_agent':
            if filtered_data['Delivery_Time'].mean() > 3:
                suggestions.append("Optimize delivery routes to reduce delivery time.")
            if filtered_data['On_Time_Delivery'].mean() < 90:
                suggestions.append("Improve scheduling and coordination to increase on-time deliveries.")
            if filtered_data['Customer_Complaints'].sum() > 50:
                suggestions.append("Investigate the causes of customer complaints and address them promptly.")
        elif stakeholder == 'logistics_manager' or stakeholder == 'general_manager':
            if filtered_data['Cycle_Time'].mean() > 5:
                suggestions.append("Consider optimizing the logistics network to reduce cycle time.")
            if filtered_data['Total_Cost'].sum() > 100000:
                suggestions.append("Review the overall logistics process to identify cost-saving opportunities.")
            if filtered_data['Employee_Productivity'].mean() < 10:
                suggestions.append("Implement productivity enhancement programs across departments.")
        elif stakeholder == 'marketing_head':
            if filtered_data['Customer_Satisfaction'].mean() < 4:
                suggestions.append("Analyze customer feedback to improve satisfaction levels.")
            if filtered_data['Customer_Complaints'].sum() > 50:
                suggestions.append("Investigate the causes of customer complaints and address them promptly.")
        elif stakeholder == 'administration_head':
            if filtered_data['Total_Cost'].sum() > 100000:
                suggestions.append("Review administrative expenses to identify cost-saving opportunities.")
            if filtered_data['Vehicle_Maintenance_Cost'].sum() > 50000:
                suggestions.append("Implement a preventive maintenance program to reduce vehicle maintenance costs.")

        return html.Ul([html.Li(suggestion) for suggestion in suggestions])

    except Exception as e:
        print(f"Error in bpr_analysis: {e}")
        return html.Ul([])

if __name__ == '__main__':
    app.run_server(debug=True, port=8051)  # Changed port to 8051