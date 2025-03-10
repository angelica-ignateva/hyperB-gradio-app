import gradio as gr
from specklepy.api.client import SpeckleClient
from specklepy.api.credentials import get_account_from_token
import pandas as pd
import plotly.express as px
import os

# Initialize Speckle client and credentials
speckle_server = "macad.speckle.xyz"
speckle_token = "abaa47aed44d2e7faf42d3ba5f7e7440a06b487d9e"
client = SpeckleClient(host=speckle_server)
account = get_account_from_token(speckle_token, speckle_server)
client.authenticate_with_account(account)

# Project ID
project_id = "28a211b286"
project = client.project.get_with_models(project_id=project_id, models_limit=100)

# Filter models whose names start with 'structure/'
# models = [item for item in project.models.items] // all models
models = [item for item in project.models.items if item.name.startswith('service/')]
model = models[0]  # Select the first model
models_name = [m.name for m in models]  # Extract model names
models_name = models_name[0]  # Select the first model
versions = client.version.get_versions(model_id=model.id, project_id=project.id, limit=100).items
version = versions[0]  # Select the first version

def version_name():
    timestamp = model.createdAt.strftime("%Y-%m-%d %H:%M:%S")
    return ' - '.join([version.authorUser.name, timestamp, version.message])

def create_viewer_url(version, project):
    embed_src = f"https://macad.speckle.xyz/projects/{project.id}/models/{model.id}@{version.id}#embed=%7B%22isEnabled%22%3Atrue%2C%7D"
    return embed_src


def plot_bar_chart(types_list, values_list):
    df = pd.DataFrame({
        'category': types_list,
        'values': values_list,
    })

    fig = px.bar(df, y='category', x='values', orientation= 'h', color='category',
                 color_discrete_sequence=px.colors.sequential.Sunsetdark_r)  # or .Viridis, .Inferno, .Magma, etc.
                # color_discrete_sequence=['#49bf66', '#1c77d9', '#7a36d9', '#c7080b', '#ff8800'])  # Custom colors
    
                
    
    fig.update_layout(
        height = 500,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        paper_bgcolor='rgb(15, 15, 15)',  # Graphite background
        plot_bgcolor='rgb(15, 15, 15)',   # Graphite plot area
        font=dict(color='white'),         # White font color
        title_font=dict(color='white'),   # White title font
        yaxis=dict(showticklabels=False), # Hide y-axis labels
        xaxis=dict(showgrid=True, gridcolor='rgb(150, 150, 150)')  # Grey vertical grid lines
    )
    
    fig.update_traces(textposition='outside')  # Display values outside bars

    return fig

def plot_pie_chart(types_list, values_list):
    df = pd.DataFrame({
        'category': types_list,
        'values': values_list,
    })

    fig = px.pie(df, names='category', values='values', hole=0.3,
                 color_discrete_sequence=px.colors.sequential.Sunsetdark)  # or .Bold, .Safe, .Vivid, etc.
                # color_discrete_sequence=['#49bf66', '#1c77d9', '#7a36d9', '#c7080b', '#ff8800'])  # Custom colors
    
                
    
    fig.update_layout(
        height = 770,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        paper_bgcolor='rgb(15, 15, 15)',  # Graphite background
        plot_bgcolor='rgb(15, 15, 15)',   # Graphite plot area
        font=dict(color='white'),         # White font color
        title_font=dict(color='white'),   # White title font
        yaxis=dict(showticklabels=False), # Hide y-axis labels
        xaxis=dict(showgrid=True, gridcolor='rgb(150, 150, 150)')  # Grey vertical grid lines
    )
    
    fig.update_traces(textposition='outside', sort = False, pull=[0.1] * len(df))  # Display values outside bars

    return fig

###########################################################################################################

# Load Google Sheet
sheet_csv_url1 = "https://docs.google.com/spreadsheets/d/1Ju7wDVKEIBMoE5DzkIIKqYtXg5rmnVC-52HSGhMYdew/export?format=csv&gid=156286963"
df1 = pd.read_csv(sheet_csv_url1)

sheet_csv_url2 = "https://docs.google.com/spreadsheets/d/1Ju7wDVKEIBMoE5DzkIIKqYtXg5rmnVC-52HSGhMYdew/export?format=csv&gid=1699500852"
df2 = pd.read_csv(sheet_csv_url2)

sheet_csv_url3 = "https://docs.google.com/spreadsheets/d/1Ju7wDVKEIBMoE5DzkIIKqYtXg5rmnVC-52HSGhMYdew/export?format=csv&gid=1882469927"
df3 = pd.read_csv(sheet_csv_url3)

###########################################################################################################

pie1 = plot_pie_chart(df1['Function'].tolist()[:-2], df1['Area, sq.m.'].tolist()[:-2])
bar2 = plot_bar_chart(df2['Amenity type'].tolist(), df2['Average time, min'].tolist())
pie3 = plot_pie_chart(df3['Description'].tolist()[:-2], df3['Area, sq.m.'].tolist()[:-2])
# pie1.show()

with gr.Blocks() as c_demo:

    with gr.Tab(label="Statictics"):

        with gr.Row(equal_height=True):
                gr.Textbox(value=models_name, label="Last Service Team Model")
                gr.Textbox(value = version_name(), label="Last Version")
        with gr.Row(equal_height=True):
            with gr.Column():
                viewer_iframe = gr.HTML()
        
            with gr.Column():
                gr.Gallery(value=["images/service_01.png", "images/service_02.png", "images/service_03.gif", "images/service_04.png"], label="Service Team Images", 
                            rows=[1], columns=[3], selected_index=0, object_fit="contain", height=600)
                    

        gr.Markdown("#", height=50)
        gr.Markdown("# Service Team Statistics", container=True)            
        with gr.Row():
            gr.DataFrame(value=df1, label="Service Team Metrics", interactive=False, show_fullscreen_button = True, max_height=1000, column_widths=[200,100])
            gr.Plot(pie1, container=False, show_label=False)
        gr.Markdown("#", height=50)

        gr.Markdown("#", height=50)
        gr.Markdown("# KPI 1: Distance to amenities", container=True)  
        with gr.Row():
            with gr.Column():
                gr.DataFrame(value=df2, label="Distance to function", interactive=False, show_fullscreen_button = True, max_height=1000, show_row_numbers=True)
                gr.Image(value="images/service_metric2.jpg", show_label=False, container=False, show_fullscreen_button=False, show_download_button=False)
            with gr.Column():
                gr.Plot(bar2, container=False, show_label=False) 

        gr.Markdown("#", height=50)
        gr.Markdown("# KPI 2: Open Space per person", container=True)  
        with gr.Row():
            with gr.Column():
                gr.DataFrame(value=df3, label="Open Space per person", interactive=False, show_fullscreen_button = True, max_height=1000)
                gr.Image(value="images/service_metric1.jpg", show_label=False, container=False, show_fullscreen_button=False, show_download_button=False)
            with gr.Column():
                gr.Plot(pie3, container=False, show_label=False)  

    with gr.Tab(label="Adjancency matrix"):
        gr.Markdown("#", height=50)
        gr.Markdown("# Adjacency matrix", container=True)
        gr.HTML(f'<iframe src="https://docs.google.com/spreadsheets/d/1Ju7wDVKEIBMoE5DzkIIKqYtXg5rmnVC-52HSGhMYdew/htmlembed?gid=28596027" width="100%" height="800px"></iframe>')
        

    # Load spekcle viewer
    def initialize_app():
        viewer_url = create_viewer_url(version, project)
        return f'<iframe src="{viewer_url}" style="width:100%; height:600px; border:none;"></iframe>'


    c_demo.load(fn=initialize_app, outputs=[viewer_iframe])

    
# c_demo.launch()

# gradio service_page.py


    