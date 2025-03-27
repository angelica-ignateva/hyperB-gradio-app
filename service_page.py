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
# models = [item for item in project.models.items] // all models
models = [item for item in project.models.items if item.name.startswith('service/')]
model = models[0]  # Select the first model
models_name = [m.name for m in models]  # Extract model names
model_name = models_name[0]  # Select the first model
versions = client.version.get_versions(model_id=model.id, project_id=project.id, limit=100).items
version = versions[0]  # Select the first version

def version_name(model, version):
    timestamp = model.createdAt.strftime("%Y-%m-%d %H:%M:%S")
    return ' - '.join([version.authorUser.name, timestamp, version.message])

def create_viewer_url(model, version):
    embed_src = f"https://macad.speckle.xyz/projects/{project_id}/models/{model.id}@{version.id}#embed=%7B%22isEnabled%22%3Atrue%2C%7D"
    iframe = f'<iframe src="{embed_src}" style="width:100%; height:750px; border:none;"></iframe>'
    return iframe


def plot_bar_chart(types_list, values_list):
    df = pd.DataFrame({
        'amenity': types_list,
        'distance to amenities (minutes)': values_list,
    })

    fig = px.bar(df, y='amenity', x='distance to amenities (minutes)', orientation= 'h', color='amenity',
                 color_discrete_sequence=px.colors.sequential.Sunsetdark_r)  # or .Viridis, .Inferno, .Magma, etc.
                # color_discrete_sequence=['#49bf66', '#1c77d9', '#7a36d9', '#c7080b', '#ff8800'])  # Custom colors
    
                
    
    fig.update_layout(
        height = 550,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        paper_bgcolor='rgb(15, 15, 15)',  # Graphite background
        plot_bgcolor='rgb(15, 15, 15)',   # Graphite plot area
        font=dict(family="Roboto Mono", size=12, color="white"),       # White font color
        title_font=dict(color='white'),   # White title font
        yaxis=dict(showticklabels=False), # Hide y-axis labels
        xaxis=dict(showgrid=True, gridcolor='rgb(150, 150, 150)')  # Grey vertical grid lines
    )
    
    fig.update_traces(textposition='outside')  # Display values outside bars

    return fig

def plot_pie_chart(types_list, values_list, title):
    df = pd.DataFrame({
        'category': types_list,
        'values': values_list,
    })

    fig = px.pie(df, names='category', values='values', hole=0.3,
                 color_discrete_sequence=px.colors.sequential.Sunsetdark)  # or .Bold, .Safe, .Vivid, etc.
                # color_discrete_sequence=['#49bf66', '#1c77d9', '#7a36d9', '#c7080b', '#ff8800'])  # Custom colors
    
                
    
    fig.update_layout(
        height = 770,
        title=dict(
            text=title,  # Setting the title text
            x=0.5,       # Center align title
            y=0.02,      # Adjust vertical positioning
            font=dict(size=18, color="white")  # Title font settings
        ),
        legend=dict(orientation="h", yanchor="bottom", y=1.03, xanchor="left", x=0),
        paper_bgcolor='rgb(15, 15, 15)',  # Graphite background
        plot_bgcolor='rgb(15, 15, 15)',   # Graphite plot area
        font=dict(family="Roboto Mono", size=10, color="white"),         # White font color
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

pie1 = plot_pie_chart(df1['Function'].tolist()[:-2], df1['Area, sq.m.'].tolist()[:-2], 'Area Distribution (%)')
bar2 = plot_bar_chart(df2['Amenity type'].tolist(), df2['time, min'].tolist())
pie3 = plot_pie_chart(df3['Description'].tolist()[:-2], df3['Area, sq.m.'].tolist()[:-2], 'Open Area Distribution (%)')
# pie1.show()

def highlight_last_row(s):
    color = 'rgba(255, 136, 0, 0.15)'  # Light blue with 50% transparency
    return [f'background-color: {color}' if i == s.index[-1] else '' for i in s.index]

# Metrics cards in a row with matching style to your dashboard
metrics_html = """
<div style="padding: 20px; font-family: 'Roboto Mono', monospace;">
    <!-- Import Roboto Mono font -->
    <link href="https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@400;500;700&display=swap" rel="stylesheet">
    
    <h1 style="color: white; margin-bottom: 30px; font-family: 'Roboto Mono', monospace; font-size: 22px;">SERVICE METRICS</h1>
    
    <div style="display: flex; flex-wrap: wrap; justify-content: space-between; gap: 20px;">
        <!-- Card A -->
        <div style="background-color: #1a1a1a; border-radius: 8px; border-top: 4px solid #ff8800; 
                    flex: 1; min-width: 180px; padding: 24px; box-shadow: 0 0 15px rgba(255, 136, 0, 0.5);">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                <div style="color: #ffffff; font-size: 16px; font-weight: 500; letter-spacing: 0.5px; font-family: 'Roboto Mono', monospace;">
                    OPEN AREA PER PERSON
                </div>
                <div style="display: flex; align-items: center;">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M12 4L12 20" stroke="#33ff33" stroke-width="2" stroke-linecap="round"/>
                        <path d="M6 10L12 4L18 10" stroke="#33ff33" stroke-width="2" stroke-linecap="round"/>
                    </svg>
                    <span style="margin-left: 5px; font-size: 14px; color: #33ff33;">33%</span>
                </div>
            </div>
            <div style="color: #ffffff; font-size: 28px; font-weight: 700; letter-spacing: 0.5px; font-family: 'Roboto Mono', monospace;">
                11.11 m²
            </div>
        </div>
        
        <!-- Card B -->
        <div style="background-color: #1a1a1a; border-radius: 8px; border-top: 4px solid #ff8800; 
                    flex: 1; min-width: 180px; padding: 24px; box-shadow: 0 0 15px rgba(255, 136, 0, 0.5);">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                <div style="color: #ffffff; font-size: 16px; font-weight: 500; letter-spacing: 0.5px; font-family: 'Roboto Mono', monospace;">
                    AVERAGE TRAVEL TIME TO ALL TYPES OF AMENITIES
                </div>
                <div style="display: flex; align-items: center;">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M12 20L12 4" stroke="#33ff33" stroke-width="2" stroke-linecap="round"/>
                        <path d="M6 14L12 20L18 14" stroke="#33ff33" stroke-width="2" stroke-linecap="round"/>
                    </svg>
                    <span style="margin-left: 5px; font-size: 14px; color: #33ff33;">25%</span>
                </div>
            </div>
            <div style="color: #ffffff; font-size: 28px; font-weight: 700; letter-spacing: 0.5px; font-family: 'Roboto Mono', monospace;">
                9min 45s
            </div>
        </div>
    </div>
</div>
"""

df1 = df1.style.apply(highlight_last_row, axis=0) # Apply the highlighting
df2 = df2.style.apply(highlight_last_row, axis=1)
df3 = df3.style.apply(highlight_last_row, axis=0) # Apply the highlighting

with gr.Blocks() as demo:

    # with gr.Tab(label="Statictics"):

    with gr.Row(equal_height=True):
            model_dropdown = gr.Dropdown(choices=models_name, label="Select Service Team Model", value = model_name)
            version_text = gr.Textbox(value = version_name(model, version), info="Last version of selected model was sent by ", container=False, lines=2)
    with gr.Row(equal_height=True):
        with gr.Column():
            viewer_iframe = gr.HTML()
    
        with gr.Column():
            gr.Gallery(value=["service_0.png", "service_00.png", "service_01.png", "service_02.png", "service_03.gif", "service_04.png"], label="Service Team Images", 
                        rows=[1], columns=[3], selected_index=0, object_fit="contain", height=750)
            
    # gr.Markdown("#", height=50)
    gr.HTML(metrics_html)
                

    gr.Markdown("#", height=50)
    gr.Markdown("## Service Team Statistics", container=True)            
    with gr.Row():
        gr.DataFrame(value=df1, label="Service Team Metrics", interactive=False, show_fullscreen_button = True, max_height=1000, column_widths=[200,100])
        gr.Plot(pie1, container=False, show_label=False)

    gr.Markdown("#", height=50)
    gr.Markdown("## KPI 1: Distance to amenities", container=True)  
    with gr.Row():
        with gr.Column(scale=1.1):
            gr.DataFrame(value=df2, label="Distance to function", interactive=False, show_fullscreen_button = True, max_height=1000, show_row_numbers=True)
        with gr.Column():
            gr.Plot(bar2, container=False, show_label=False) 

    gr.Markdown("#", height=50)
    gr.Markdown("## KPI 2: Open Space per person", container=True)  
    with gr.Row():
        with gr.Column():
            gr.DataFrame(value=df3, label="Open Space per person", interactive=False, show_fullscreen_button = True, max_height=1000)
        with gr.Column():
            gr.Plot(pie3, container=False, show_label=False)  

    # with gr.Tab(label="Adjancency matrix"):
    #     gr.Markdown("#", height=50)
    #     gr.Markdown("# Adjacency matrix", container=True)
    #     gr.HTML(f'<iframe src="https://docs.google.com/spreadsheets/d/1Ju7wDVKEIBMoE5DzkIIKqYtXg5rmnVC-52HSGhMYdew/htmlembed?gid=28596027" width="100%" height="800px"></iframe>')
        

    # Load spekcle viewer
    def initialize_app():
        viewer_url = create_viewer_url(model, version)
        return viewer_url


    demo.load(fn=initialize_app, outputs=[viewer_iframe])

    def handle_model_change(selected_model_name):
        selected_model = next((m for m in models if m.name == selected_model_name), None)
        if not selected_model:
            return '<p>Model not found</p>'
        version = client.version.get_versions(model_id=selected_model.id, project_id=project.id, limit=5).items[0]
        return create_viewer_url(selected_model, version), version_name(selected_model, version)


    # Event handlers
    model_dropdown.change(fn=handle_model_change, inputs=model_dropdown, outputs=[viewer_iframe, version_text])

    
demo.launch()

# gradio service_page.py


    