import gradio as gr
from specklepy.api.client import SpeckleClient
from specklepy.api.credentials import get_account_from_token
import pandas as pd
from config import speckle_token

from program import p_demo
from residential_page import r_demo
from service_page import s_demo
from industrial_page import i_demo
from facade_page import f_demo
from structural_page import st_demo

js_func = """
function refresh() {
    const url = new URL(window.location);
    if (url.searchParams.get('__theme') !== 'dark') {
        url.searchParams.set('__theme', 'dark');
        window.location.href = url.href;
    }
}
"""

# Dashboard description with Roboto Mono font
dashboard_description = """
<div style="font-family: 'Roboto Mono', monospace; margin-top: -30px;">
    <h1 style="font-size: 18px;">HYPER-B // DASHBOARD OVERVIEW</h1>

    <div style="font-size: 14px; line-height: 1.5;">
    This dashboard is a Gradio-based interface designed to monitor and analyse the activity and objectives of each design team within the BIMSC Studio HYPER-B building team. Data is organised into tabs that serve a specific analytical purpose.

    The dashboard was originally created as a collaborative tool to monitor Speckle commits from each design team and was expanded to encompass analysis of team-specific key performance indicators (KPIs) to facilitate our overall building narrative, which is the design of a closed-loop system.
    </div>

    <h1 style="font-size: 18px;">HYPER-B // APPROACH</h1>

    <div style="font-size: 14px; line-height: 1.5;">
    In our approach to implement a closed-loop system, we refer to Paolo Soleri's 1969 vision of Arcology - a fusion between Architecture and Ecology to create efficient and sustainable urban environments that seeks to maximise population density while minimising environmental impact. We use this theoretical framework in our approach to KPIs. In doing so, we define several team-specific objectives that are analysed and presented as metrics for each design team, which can be queried on the dashboard.
    </div>
</div>
"""



# Metrics cards in a row with matching style to your dashboard
metrics_html = """
<div style="padding: 20px; font-family: 'Roboto Mono', monospace;">
    <!-- Import Roboto Mono font -->
    <link href="https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@400;500;700&display=swap" rel="stylesheet">
    
    <h1 style="color: white; margin-bottom: 30px; font-family: 'Roboto Mono', monospace; font-size: 18px;">OVERALL BUILDING METRICS</h1>
    
    <div style="display: flex; flex-wrap: wrap; justify-content: space-between; gap: 20px;">
        <!-- Card 1: Tower GFA -->
        <div style="background-color: #1a1a1a; border-radius: 8px; border-top: 4px solid #ff0066; 
                    flex: 1; min-width: 180px; padding: 24px; box-shadow: 0 0 15px rgba(255, 0, 102, 0.2);">
            <div style="color: #ffffff; font-size: 16px; font-weight: 500; margin-bottom: 12px; letter-spacing: 0.5px; font-family: 'Roboto Mono', monospace;">
                TOWER GFA
            </div>
            <div style="color: #ffffff; font-size: 28px; font-weight: 700; letter-spacing: 0.5px; font-family: 'Roboto Mono', monospace;">
                450k m²
            </div>
        </div>
        
        <!-- Card 2: Tallest Tower -->
        <div style="background-color: #1a1a1a; border-radius: 8px; border-top: 4px solid #ff0066; 
                    flex: 1; min-width: 180px; padding: 24px; box-shadow: 0 0 15px rgba(255, 0, 102, 0.2);">
            <div style="color: #ffffff; font-size: 16px; font-weight: 500; margin-bottom: 12px; letter-spacing: 0.5px; font-family: 'Roboto Mono', monospace;">
                TALLEST TOWER
            </div>
            <div style="color: #ffffff; font-size: 28px; font-weight: 700; letter-spacing: 0.5px; font-family: 'Roboto Mono', monospace;">
                280 m
            </div>
        </div>
        
        <!-- Card 3: Tower Floors -->
        <div style="background-color: #1a1a1a; border-radius: 8px; border-top: 4px solid #ff0066; 
                    flex: 1; min-width: 180px; padding: 24px; box-shadow: 0 0 15px rgba(255, 0, 102, 0.2);">
            <div style="color: #ffffff; font-size: 16px; font-weight: 500; margin-bottom: 12px; letter-spacing: 0.5px; font-family: 'Roboto Mono', monospace;">
                TALLEST TOWER
            </div>
            <div style="color: #ffffff; font-size: 28px; font-weight: 700; letter-spacing: 0.5px; font-family: 'Roboto Mono', monospace;">
                60 FLOORS
            </div>
        </div>
        
        <!-- Card 4: Inhabitants -->
        <div style="background-color: #1a1a1a; border-radius: 8px; border-top: 4px solid #ff0066; 
                    flex: 1; min-width: 180px; padding: 24px; box-shadow: 0 0 15px rgba(255, 0, 102, 0.2);">
            <div style="color: #ffffff; font-size: 16px; font-weight: 500; margin-bottom: 12px; letter-spacing: 0.5px; font-family: 'Roboto Mono', monospace;">
                NUMBER OF INHABITANTS
            </div>
            <div style="color: #ffffff; font-size: 28px; font-weight: 700; letter-spacing: 0.5px; font-family: 'Roboto Mono', monospace;">
                6208
            </div>
        </div>

        <!-- Card 5: Inhabitants -->
        <div style="background-color: #1a1a1a; border-radius: 8px; border-top: 4px solid #ff0066; 
                    flex: 1; min-width: 180px; padding: 24px; box-shadow: 0 0 15px rgba(255, 0, 102, 0.2);">
            <div style="color: #ffffff; font-size: 16px; font-weight: 500; margin-bottom: 12px; letter-spacing: 0.5px; font-family: 'Roboto Mono', monospace;">
                LOWEST TOWER
            </div>
            <div style="color: #ffffff; font-size: 28px; font-weight: 700; letter-spacing: 0.5px; font-family: 'Roboto Mono', monospace;">
                200 m
            </div>
        </div>

        <!-- Card 6: Inhabitants -->
        <div style="background-color: #1a1a1a; border-radius: 8px; border-top: 4px solid #ff0066; 
                    flex: 1; min-width: 180px; padding: 24px; box-shadow: 0 0 15px rgba(255, 0, 102, 0.2);">
            <div style="color: #ffffff; font-size: 16px; font-weight: 500; margin-bottom: 12px; letter-spacing: 0.5px; font-family: 'Roboto Mono', monospace;">
                LOWEST TOWER
            </div>
            <div style="color: #ffffff; font-size: 28px; font-weight: 700; letter-spacing: 0.5px; font-family: 'Roboto Mono', monospace;">
                48 FLOORS
            </div>
        </div>
    </div>
</div>
"""
header_html = """
<div style="padding: 20px; font-family: 'Roboto Mono', monospace; margin-bottom: 5px;">
    <h1 style="color: white; margin-bottom: 10px; font-family: 'Roboto Mono', monospace; font-size: 18px; margin-bottom: 12px;">TEAM METRICS AND KPIs</h1>
</div>
"""

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


# Initialize Speckle client and credentials
speckle_server = "macad.speckle.xyz"
client = SpeckleClient(host=speckle_server)
account = get_account_from_token(speckle_token, speckle_server)
client.authenticate_with_account(account)
project_id = "28a211b286"
project = client.project.get_with_models(project_id=project_id, models_limit=100)

# Function to update viewer and stats
def create_viewer_url(model_name):
    # Find the model in the project
    model = next((m for m in project.models.items if m.name == model_name), None)
    if model:
        versions = client.version.get_versions(model_id=model.id, project_id=project_id, limit=1).items
        if versions:
            version = versions[0]
            embed_src = f"https://macad.speckle.xyz/projects/{project_id}/models/{model.id}@{version.id}#embed=%7B%22isEnabled%22%3Atrue%2C%7D"
            return f'<iframe src="{embed_src}" style="width:100%; height:750px; border:none;"></iframe>'
        else:
            return "No versions found for this model."
    else:
        return "Model not found."

# Add this function to filter models by team selection
def update_model_selection_by_team(team_selection):
    models = project.models.items

    if team_selection == "Residential":
        filtered_models = [m.name for m in models if m.name.startswith('residential/share')]
    elif team_selection == "Structure":
        filtered_models = [m.name for m in models if m.name.startswith('structure/share')]
    elif team_selection == "Service":
        filtered_models = [m.name for m in models if m.name.startswith('service')]
    elif team_selection == "Facade":
        filtered_models = [m.name for m in models if m.name.startswith('facade')]
    elif team_selection == "Industrial":
        filtered_models = [m.name for m in models if m.name.startswith('industrial')]
    elif team_selection == "Data":
        filtered_models = [m.name for m in models if m.name.startswith('data')]

    return gr.Dropdown(choices=filtered_models, label="Select Model", container=False)

iframe_html = '''
<iframe 
  src = "https://macad.speckle.xyz/projects/28a211b286/models/2e045c057c,355ba25602,38d2a00393,5096ad6f65,627006f015,74a5650a9f,79c2d14397,92536e4925,a73451f397,fb246c4f0e#embed=%7B%22isEnabled%22%3Atrue%2C%7D" 
  style="width:100%; height:775px; border:none;">
</iframe>
'''

# Requirements sheet
sheet_csv_urls = {
    "Residential": "https://docs.google.com/spreadsheets/d/1yZRMx0Reso1ye_OGvZoSC9BE_jwYAZAtmm9w8U0fqUs/export?format=csv",
    "Service": "https://docs.google.com/spreadsheets/d/1u6Sm7_eCTxN5gY4GMqggZG4zdgEhLy67BjkcpkVXg3A/export?format=csv",
    "Facade": "https://docs.google.com/spreadsheets/d/1TbWJKI39oWrXVW4r8LoieRx9nuRdEQvuUVe-rXqotrc/export?format=csv",
    "Structure": "https://docs.google.com/spreadsheets/d/1uIBeQa6y3gfS6D8nsHesmj9GVSo7UBWNGTdi6NM4oak/export?format=csv",
    "Industrial": "https://docs.google.com/spreadsheets/d/1dxIEr_TIosqf5fb8_GNUxXZuG6WDWhnEfhcFtiDnY_I/export?format=csv",
}

def load_sheet(team):
    if team in sheet_csv_urls:
        df = pd.read_csv(sheet_csv_urls[team])
        return df


# , text_size="lg")
with gr.Blocks(css=custom_css, js=js_func, theme=gr.themes.Default(primary_hue="indigo")) as demo:
    with gr.Tab("Hyper B"):
        with gr.Row():
            with gr.Column():
                # Add global font import
                gr.HTML(f"<style>{custom_css}</style>")
                gr.HTML(dashboard_description)
                # Your metrics cards
                gr.HTML(metrics_html)
            with gr.Column():
                gr.Markdown("#", height=25)
                # Add global font import
                gr.HTML(iframe_html)
        gr.Markdown("#", height=25)
        gr.Markdown("## TEAM MODELS & METRICS")
        with gr.Row():
            with gr.Column():
                viewer_iframe = gr.HTML()

            with gr.Column():
                models_res = [item for item in project.models.items if item.name.startswith('residential/')]
                models_name_res = [m.name for m in models_res]
                models_name_res = [name.split('/', 1)[1] if '/' in name else name for name in models_name_res]
                gr.Markdown(":Select a team to view", rtl = True)
                team_dropdown = gr.Dropdown(choices=["Residential", "Structure", "Service", "Facade", "Industrial", "Data"], label="Select Team", value="Residential", 
                                            container=False)
                gr.Markdown(":Select a team's model", rtl = True)
                model_dropdown = update_model_selection_by_team("Residential")

                gr.Markdown("#", height=50)
                gr.Markdown("### TEAM METRICS")
                sheet_display = gr.DataFrame(show_row_numbers=True, column_widths=["50%","50%"])
                team_dropdown.change(fn=load_sheet, inputs=team_dropdown, outputs=sheet_display)

    with gr.Tab("Program Overview"):
        p_demo.render()
    with gr.Tab("Residential Team"):
        r_demo.render()
    with gr.Tab("Service Team"):
        s_demo.render()
    with gr.Tab("Industrial Team"):
        i_demo.render()
    with gr.Tab("Structural Team"):
        st_demo.render()
    with gr.Tab("Facade Team"):
        f_demo.render()

    # Load spekcle viewer
    def initialize_app():
        viewer_url = create_viewer_url('residential/shared/unit_exterior_walls')
        return viewer_url


    demo.load(fn=initialize_app, outputs=[viewer_iframe])
    demo.load(fn=load_sheet, inputs=team_dropdown, outputs=sheet_display)


    # Event handlers
    team_dropdown.change(
        fn=update_model_selection_by_team,
        inputs=team_dropdown,
        outputs=[model_dropdown]
    )

    model_dropdown.change(
        fn=create_viewer_url,
        inputs=[model_dropdown],
        outputs=viewer_iframe
    )

    # Rest of your dashboard...

demo.launch()

# gradio app.py