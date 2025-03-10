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
# models = [item for item in project.models.items]
models = [item for item in project.models.items if item.name.startswith('industrial/place holder/massing')]
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


############################################################################################################
####Load Meshes#############################################################################################

# def load_mesh():
#     model_path_1 = os.path.join(os.path.dirname(__file__), "files/residential_views.glb")  # First 3D model
#     model_path_2 = os.path.join(os.path.dirname(__file__), "files/residential_solar.glb")   # Second 3D model
#     return model_path_1, model_path_2

############################################################################################################
####GRAPHS##################################################################################################

def plot_pie_chart(value1):
    value2 = 100.0-value1
    df = pd.DataFrame({
        'category': ['Local food fed residents', 'Residents with combined diet'],
        'values': [value1, value2]
    })
    
    fig = px.pie(df, values='values', names='category', title="Local food diet residents ratio", hole=0.3,
                 color_discrete_sequence=['#83de9d', '#2f984d'])
    fig.update_traces(textposition='outside', textinfo='percent+label')
    
    fig.update_layout(
        paper_bgcolor='rgb(15, 15, 15)',  # Graphite background color
        plot_bgcolor='rgb(15, 15, 15)',   # Graphite background color for the plot area
        font=dict(color='white'),          # Font color for better contrast
        title_font=dict(color='white'),
        showlegend=False,
        height=700   
    )

    return fig

###########################################################################################################


with gr.Blocks() as i_demo:

    with gr.Row(equal_height=True):
            gr.Textbox(value=models_name, label="Last Industrial Team Model")
            gr.Textbox(value = version_name(), label="Last Version")
    with gr.Row(equal_height=True):
        with gr.Column():
            viewer_iframe = gr.HTML()
    
        with gr.Column():
            gr.Gallery(value=["images/industrial_01.gif", "images/industrial_02.png", "images/industrial_03.png"], label="Industrial Team Images", 
                        rows=[1], columns=[3], selected_index=0, object_fit="contain", height=600)
                

    gr.Markdown("#", height=50)
    gr.Markdown("# KPIs and metrics", container=True)  
    gr.Markdown("## Industry Data")
    with gr.Row(equal_height=True):
            gr.Image(value="images/industrial_metric1.jpg", show_label=False, show_download_button=False, show_fullscreen_button=False, container=False)
            gr.Image(value="images/industrial_metric2.jpg", show_label=False, show_download_button=False, show_fullscreen_button=False, container=False)
            gr.Image(value="images/industrial_metric3.jpg", show_label=False, show_download_button=False, show_fullscreen_button=False, container=False)
            gr.Image(value="images/industrial_metric4.jpg", show_label=False, show_download_button=False, show_fullscreen_button=False, container=False)

    gr.Markdown("#", height=50)
    gr.Markdown("# KPI 1: Percentage of local food fed residents", container=True)  
    with gr.Row(equal_height=True):
        with gr.Column():
            gr.Number(label='Amount of people fed with local production', value=5413)
            gr.Number(label='Growing area required to feed one person(m2)', value=3.5)
            gr.Textbox(label='Growing area to fishtank volume ratio', value='5:1')
            value1 = gr.Number(label="Percentage of people having local food diet (assuming 11000 residents)", value=49)
            gr.Image(value="images/industrial_metric5.jpg", show_label=False, show_download_button=False, show_fullscreen_button=False, container=False)
        

        with gr.Column(scale=2):
            output1 = gr.Plot(show_label=False, container=False)
            

    # Load spekcle viewer
    def initialize_app():
        viewer_url = create_viewer_url(version, project)
        return f'<iframe src="{viewer_url}" style="width:100%; height:600px; border:none;"></iframe>'


    i_demo.load(fn=initialize_app, outputs=[viewer_iframe])
    

    # Automatically generate plots
    i_demo.load(plot_pie_chart, inputs=value1, outputs=output1)
    
# i_demo.launch()

# gradio industrial_page.py


    