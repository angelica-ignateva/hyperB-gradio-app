import gradio as gr
from specklepy.api.client import SpeckleClient
from specklepy.api.credentials import get_account_from_token
import pandas as pd
import plotly.express as px
from config import speckle_token

# Initialize Speckle client and credentials
speckle_server = "macad.speckle.xyz"
client = SpeckleClient(host=speckle_server)
account = get_account_from_token(speckle_token, speckle_server)
client.authenticate_with_account(account)

# Project ID
project_id = "28a211b286"
project = client.project.get_with_models(project_id=project_id, models_limit=100)

# Filter models whose names start with 'structure/'
# models = [item for item in project.models.items]
models = [item for item in project.models.items if item.name.startswith('facade')]
model = [item for item in project.models.items if item.name.startswith('facade/final panelisation')][0]  # Select the first model
models_name = [m.name for m in models]  # Extract model names
model_name = model.name  # Select the first model
versions = client.version.get_versions(model_id=model.id, project_id=project.id, limit=100).items
version = versions[0]  # Select the first version

model_massing = [item for item in project.models.items if item.name.startswith('structure/share/towers/v3/column')][0]
version_massing = client.version.get_versions(model_id=model_massing.id, project_id=project.id, limit=100).items[0]

##################################################

def version_name(model, version):
    timestamp = model.createdAt.strftime("%Y-%m-%d %H:%M:%S")
    return ' - '.join([version.authorUser.name, timestamp, version.message])

def create_viewer_url(model, version):
    embed_src = f"https://macad.speckle.xyz/projects/{project_id}/models/{model.id}@{version.id}#embed=%7B%22isEnabled%22%3Atrue%2C%7D"
    iframe = f'<iframe src="{embed_src}" style="width:100%; height:750px; border:none;"></iframe>'
    return iframe

# Plotting functions
def plot_pie_chart(types_list, values_list):
    df = pd.DataFrame({
        'facade type': types_list,
        'percentage': values_list,
    })

    fig = px.pie(df, names='facade type', values='percentage', hole=0.3, 
                 color_discrete_sequence=px.colors.sequential.Sunsetdark)  # or .Bold, .Safe, .Vivid, etc.
                # color_discrete_sequence=['#49bf66', '#1c77d9', '#7a36d9', '#c7080b', '#ff8800'])  # Custom colors
    
                
    
    fig.update_layout(
        height = 770,
        title=dict(
            text='Facade Type Distribution',  # Setting the title text
            x=0.5,       # Center align title
            y=0.02,      # Adjust vertical positioning
            font=dict(size=18, color="white")  # Title font settings
        ),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        paper_bgcolor='rgb(15, 15, 15)',  # Graphite background
        plot_bgcolor='rgb(15, 15, 15)',   # Graphite plot area
        font=dict(family="Roboto Mono", size=10, color="white"),         # White font color
        yaxis=dict(showticklabels=False), # Hide y-axis labels
        xaxis=dict(showgrid=True, gridcolor='rgb(150, 150, 150)')  # Grey vertical grid lines
    )
    
    fig.update_traces(textposition='outside', sort = False, pull=[0.1] * len(df))  # Display values outside bars

    return fig


##################################################

sheet_csv_url1 = "https://docs.google.com/spreadsheets/d/1Ju7wDVKEIBMoE5DzkIIKqYtXg5rmnVC-52HSGhMYdew/export?format=csv&gid=451167349"
df1 = pd.read_csv(sheet_csv_url1)
bar1 = plot_pie_chart(df1['NAME'][:-1].tolist(), df1['%'][:-1].tolist())

def highlight_last_row(s):
    color = 'rgba(101, 44, 179, 0.25)'  # Light blue with 50% transparency
    return [f'background-color: {color}' if i == s.index[-1] else '' for i in s.index]

# Apply the highlighting
styler = df1.style.apply(highlight_last_row, axis=0)


##################################################

# Metrics cards in a row with matching style to your dashboard
metric1_html = """
<div style="padding: 20px; font-family: 'Roboto Mono', monospace;">
    <!-- Import Roboto Mono font -->
    <link href="https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@400;500;700&display=swap" rel="stylesheet">
    
    <h1 style="color: white; margin-bottom: 30px; font-family: 'Roboto Mono', monospace; font-size: 18px;">KPI METRIC</h1>
    
    <div style="display: flex; flex-wrap: wrap; justify-content: space-between; gap: 20px;">
        <!-- Card A -->
        <div style="background-color: #1a1a1a; border-radius: 8px; border-top: 4px solid #652cb3; 
                    flex: 1; min-width: 180px; padding: 24px; box-shadow: 0 0 15px rgba(101, 44, 179, 0.5);">
            <div style="color: #ffffff; font-size: 16px; font-weight: 500; margin-bottom: 12px; letter-spacing: 0.5px; font-family: 'Roboto Mono', monospace;">
                ENERGY GENERATION
            </div>
            <div style="color: #ffffff; font-size: 28px; font-weight: 700; letter-spacing: 0.5px; font-family: 'Roboto Mono', monospace;">
                57.2%
            </div>
        </div>

    </div>
</div>
"""


# GRADIO UI
with gr.Blocks() as f_demo:
    with gr.Row(equal_height=True):
        model_dropdown = gr.Dropdown(choices=models_name, label="Select Facade Team Model", value = model_name)
        version_text = gr.Textbox(value = version_name(model, version), info="Last version of selected model was sent by ", container=False, lines=2)
    with gr.Row(equal_height=True):
        with gr.Column():
            viewer_iframe = gr.HTML()
        with gr.Column():
            gr.Gallery(value=["facade_00.png", "facade_01.png", "facade_02.png", "facade_03.png"], label="Facade Images", 
                            rows=[1], columns=[3], selected_index=0, object_fit="contain", height=750)
    
    gr.Markdown("#", height=50)
    gr.Markdown("## KPI: Energy generation", container=True)
    with gr.Row():
        with gr.Column(scale=1.5):
            gr.DataFrame(value=styler, label="Facade Distribution Data", interactive=False, show_fullscreen_button = True, max_height=1000, column_widths=[90,10, 15, 15])
            gr.HTML(metric1_html)
        with gr.Column():
            gr.Plot(bar1, container=False, show_label=False)

    # Load spekcle viewer
    def initialize_app():
        viewer_url = create_viewer_url(model, version)
        return viewer_url


    f_demo.load(fn=initialize_app, outputs=[viewer_iframe])

    def handle_model_change(selected_model_name):
        selected_model = next((m for m in models if m.name == selected_model_name), None)
        if not selected_model:
            return '<p>Model not found</p>'
        version = client.version.get_versions(model_id=selected_model.id, project_id=project.id, limit=5).items[0]
        return create_viewer_url(selected_model, version), version_name(selected_model, version)


    # Event handlers
    model_dropdown.change(fn=handle_model_change, inputs=model_dropdown, outputs=[viewer_iframe, version_text])
    

# demo.launch()

# gradio facade_page.py