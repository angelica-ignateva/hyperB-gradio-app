import gradio as gr
from specklepy.api.client import SpeckleClient
from specklepy.api.credentials import get_account_from_token
import pandas as pd
import plotly.express as px
from config import speckle_token

# Custom CSS for font and hiding scrollbars
custom_css = """
/* Import Roboto Mono font */
@import url('https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@400;500;700&display=swap');

/* Hide scrollbars for Chrome, Safari, and Opera */
.gradio-container *::-webkit-scrollbar {
  display: none !important;
  width: 0 !important;
  height: 0 !important;
}

/* Hide scrollbars for IE, Edge, and Firefox */
.gradio-container * {
  -ms-overflow-style: none !important;  /* IE and Edge */
  scrollbar-width: none !important;  /* Firefox */
}

/* Fix potential overflow issues while ensuring content is still accessible */
.gradio-container [data-testid="table"],
.gradio-container .gradio-dataframe,
.gradio-container .table-wrap,
.gradio-container .scroll-container {
  overflow: hidden !important;
}

/* Handle any fixed height elements that might trigger scrollbars */
.gradio-container .fixed-height {
  max-height: none !important;
}

/* Apply Roboto Mono to all elements */
body, h1, h2, h3, p, div, span, button, input, select, textarea {
  font-family: 'Roboto Mono', monospace !important;
}
"""

# Metrics cards in a row with matching style to your dashboard
metrics_html = """
<div style="padding: 20px; font-family: 'Roboto Mono', monospace;">
    <!-- Import Roboto Mono font -->
    <link href="https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@400;500;700&display=swap" rel="stylesheet">
    
    <h1 style="color: white; margin-bottom: 30px; font-family: 'Roboto Mono', monospace; font-size: 22px;">INDUSTRIAL METRICS</h1>
    
    <div style="display: flex; flex-wrap: wrap; justify-content: space-between; gap: 20px;">
        <!-- Card 1 -->
        <div style="background-color: #1a1a1a; border-radius: 8px; border-top: 4px solid #338547; 
                    flex: 1; min-width: 180px; padding: 24px; box-shadow: 0 0 15px rgba(51, 133, 71, 0.5);">
            <div style="color: #ffffff; font-size: 16px; font-weight: 500; margin-bottom: 12px; letter-spacing: 0.5px; font-family: 'Roboto Mono', monospace;">
                NUMBER OF AQUAPONICS COLUMNS
            </div>
            <div style="color: #ffffff; font-size: 28px; font-weight: 700; letter-spacing: 0.5px; font-family: 'Roboto Mono', monospace;">
                13 403
            </div>
        </div>
        
        <!-- Card 2 -->
        <div style="background-color: #1a1a1a; border-radius: 8px; border-top: 4px solid #338547; 
                    flex: 1; min-width: 180px; padding: 24px; box-shadow: 0 0 15px rgba(51, 133, 71, 0.5);">
            <div style="color: #ffffff; font-size: 16px; font-weight: 500; margin-bottom: 12px; letter-spacing: 0.5px; font-family: 'Roboto Mono', monospace;">
                NUMBER OF PLANTERS
            </div>
            <div style="color: #ffffff; font-size: 28px; font-weight: 700; letter-spacing: 0.5px; font-family: 'Roboto Mono', monospace;">
                603 135
            </div>
        </div>
        
        <!-- Card 3 -->
        <div style="background-color: #1a1a1a; border-radius: 8px; border-top: 4px solid #338547; 
                    flex: 1; min-width: 180px; padding: 24px; box-shadow: 0 0 15px rgba(51, 133, 71, 0.5);">
            <div style="color: #ffffff; font-size: 16px; font-weight: 500; margin-bottom: 12px; letter-spacing: 0.5px; font-family: 'Roboto Mono', monospace;">
                TOTAL GROWING AREA
            </div>
            <div style="color: #ffffff; font-size: 28px; font-weight: 700; letter-spacing: 0.5px; font-family: 'Roboto Mono', monospace;">
                18 948 m²
            </div>
        </div>
        
        <!-- Card 4 -->
        <div style="background-color: #1a1a1a; border-radius: 8px; border-top: 4px solid #338547; 
                    flex: 1; min-width: 180px; padding: 24px; box-shadow: 0 0 15px rgba(51, 133, 71, 0.5);">
            <div style="color: #ffffff; font-size: 16px; font-weight: 500; margin-bottom: 12px; letter-spacing: 0.5px; font-family: 'Roboto Mono', monospace;">
                TOTAL FISHTANK VOLUME
            </div>
            <div style="color: #ffffff; font-size: 28px; font-weight: 700; letter-spacing: 0.5px; font-family: 'Roboto Mono', monospace;">
                3 789 m³
            </div>
        </div>

    </div>
</div>
"""

# Metrics cards in a row with matching style to your dashboard
metric1_html = """
<div style="padding: 20px; font-family: 'Roboto Mono', monospace;">
    <!-- Import Roboto Mono font -->
    <link href="https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@400;500;700&display=swap" rel="stylesheet">
    
    <h1 style="color: white; margin-bottom: 30px; font-family: 'Roboto Mono', monospace; font-size: 18px;">KPI METRIC</h1>
    
    <div style="display: flex; flex-wrap: wrap; justify-content: space-between; gap: 20px;">
        <!-- Card A -->
        <div style="background-color: #1a1a1a; border-radius: 8px; border-top: 4px solid #338547; 
                    flex: 1; min-width: 180px; padding: 24px; box-shadow: 0 0 15px rgba(51, 133, 71, 0.5);">
            <div style="color: #ffffff; font-size: 16px; font-weight: 500; margin-bottom: 12px; letter-spacing: 0.5px; font-family: 'Roboto Mono', monospace;">
                LOCAL FOOD FED RESIDENTS
            </div>
            <div style="color: #ffffff; font-size: 28px; font-weight: 700; letter-spacing: 0.5px; font-family: 'Roboto Mono', monospace;">
                87.2%
            </div>
        </div>

    </div>
</div>
"""

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
models = [item for item in project.models.items if item.name.startswith('industrial')]
model = [item for item in project.models.items if item.name.startswith('industrial/podium/full')][0]  # Select the first model
models_name = [m.name for m in models]  # Extract model names
model_name = model.name  # Select the first model
versions = client.version.get_versions(model_id=model.id, project_id=project.id, limit=100).items
version = versions[0]  # Select the first version

def version_name(model, version):
    timestamp = model.createdAt.strftime("%Y-%m-%d %H:%M:%S")
    return ' - '.join([version.authorUser.name, timestamp, version.message])

def create_viewer_url(model, version):
    embed_src = f"https://macad.speckle.xyz/projects/{project_id}/models/{model.id}@{version.id}#embed=%7B%22isEnabled%22%3Atrue%2C%7D"
    iframe = f'<iframe src="{embed_src}" style="width:100%; height:750px; border:none;"></iframe>'
    return iframe

def plot_pie_chart(value1, value2):
    df = pd.DataFrame({
        'category': ['Local food fed residents', 'Residents with combined diet'],
        'values': [value1, value2]
    })
    
    fig = px.pie(df, values='values', names='category', hole=0.3,
                 color_discrete_sequence=['#83de9d', '#2f984d'])
    fig.update_traces(textposition='outside', textinfo='percent+label')
    
    fig.update_layout(
        title=dict(
            text="Locally-fed Residents Ratio",  # Setting the title text
            x=0.5,       # Center align title
            y=0.02,      # Adjust vertical positioning
            font=dict(size=18, color="white")  # Title font settings
        ),
        paper_bgcolor='rgb(15, 15, 15)',  # Graphite background color
        plot_bgcolor='rgb(15, 15, 15)',   # Graphite background color for the plot area
        font=dict(family="Roboto Mono", size=14, color="white"),
        showlegend=False,
        height=700   
    )

    return fig

###########################################################################################################


with gr.Blocks(css=custom_css, theme=gr.themes.Default(primary_hue="indigo", text_size="lg")) as i_demo:

    with gr.Row(equal_height=True):
            model_dropdown = gr.Dropdown(choices=models_name, label="Select Industrial Team Model", value = model_name)
            version_text = gr.Textbox(value = version_name(model, version), info="Last version of selected model was sent by ", container=False, lines=2)
    with gr.Row(equal_height=True):
        with gr.Column():
            viewer_iframe = gr.HTML()
    
        with gr.Column():
            gr.Gallery(value=["industrial_01.gif", "industrial_01.png", "industrial_02.png", "industrial_03.png"], label="Industrial Team Images", 
                        rows=[1], columns=[3], selected_index=0, object_fit="contain", height=750)
                

    gr.Markdown("#", height=50)
    # gr.HTML(f"<style>{custom_css}</style>")
    gr.HTML(metrics_html)

    gr.Markdown("#", height=50)
    gr.Markdown("##  KPI: Percentage of local food fed residents", container=True)
    with gr.Row(equal_height=True):
        with gr.Column(variant='compact'):
            gr.HTML(metric1_html)
            gr.Number(label='People fed with local production', value=5413)
            gr.Number(label='Growing area in m² per person', value=3.5)
            gr.Textbox(label='Growing area to fishtank volume', value='5:1')
            value1 = gr.Number(label="People having local food diet", value=87.2, visible=False)
            value2 = gr.Number(label="Others)", value=12.8, visible=False)
        

        with gr.Column(scale=2):
            output1 = gr.Plot(show_label=False, container=False)
            

    # Load spekcle viewer
    def initialize_app():
        viewer_url = create_viewer_url(model, version)
        return viewer_url


    i_demo.load(fn=initialize_app, outputs=[viewer_iframe])
    

    # Automatically generate plots
    i_demo.load(plot_pie_chart, inputs=[value1, value2], outputs=output1)

    def handle_model_change(selected_model_name):
        selected_model = next((m for m in models if m.name == selected_model_name), None)
        if not selected_model:
            return '<p>Model not found</p>'
        version = client.version.get_versions(model_id=selected_model.id, project_id=project.id, limit=5).items[0]
        return create_viewer_url(selected_model, version), version_name(selected_model, version)


    # Event handlers
    model_dropdown.change(fn=handle_model_change, inputs=model_dropdown, outputs=[viewer_iframe, version_text])
    
# i_demo.launch()

# gradio industrial_page.py


    