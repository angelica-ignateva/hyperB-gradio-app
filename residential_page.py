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
models = [item for item in project.models.items if item.name.startswith('residential/shared/units_placed')]
model = models[0]  # Select the first model
model_views = [item for item in project.models.items if item.name.startswith('residential/shared/units_facade')][0]
model_solar = [item for item in project.models.items if item.name.startswith('residential/shared/units_sun_hours')][0]
models_name = [m.name for m in models]  # Extract model names
models_name = models_name[0]  # Select the first model
versions = client.version.get_versions(model_id=model.id, project_id=project.id, limit=100).items
version_unit = versions[0]  # Select the first version
version_views = client.version.get_versions(model_id=model_views.id, project_id=project_id, limit=100).items[0]
version_solar = client.version.get_versions(model_id=model_solar.id, project_id=project.id, limit=100).items[0]

def version_name(version):
    timestamp = model.createdAt.strftime("%Y-%m-%d %H:%M:%S")
    return ' - '.join([version.authorUser.name, timestamp, version.message])

def create_viewer_url(model, version):
    embed_src = f"https://macad.speckle.xyz/projects/{project_id}/models/{model.id}@{version.id}#embed=%7B%22isEnabled%22%3Atrue%2C%7D"
    iframe = f'<iframe src="{embed_src}" style="width:100%; height:750px; border:none;"></iframe>'
    return iframe



############################################################################################################
####Load Meshes#############################################################################################

def load_mesh():
    model_path_1 = os.path.join(os.path.dirname(__file__), "files/residential_UNITS.glb")  # First 3D model
    model_path_2 = os.path.join(os.path.dirname(__file__), "files/residential_solar.glb")   # Second 3D model
    return model_path_1

############################################################################################################
####KPIS and metrics########################################################################################

def plot_bar_chart(value1, value2, value3, value4):
    df = pd.DataFrame({
        'unit_type': [
            'Best views', 
            'Pleasant views',
            'Average views',
            'Worst views'
        ],
        'values': [value1, value2, value3, value4]
    })
    
    fig = px.bar(df, y='unit_type', x='values', title="Daylight Factor", 
                 color='unit_type', orientation='h',
                 color_discrete_sequence=['#04bed0', '#264ba3', '#7b258c', '#d6046d'])  # Custom colors
    
    fig.update_layout(
        height = 530,
        paper_bgcolor='rgb(15, 15, 15)',  # Graphite background
        plot_bgcolor='rgb(15, 15, 15)',   # Graphite plot area
        font=dict(color='white'),         # White font color
        title_font=dict(color='white'),   # White title font
        yaxis=dict(showticklabels=False), # Hide y-axis labels
        xaxis=dict(showgrid=True, gridcolor='rgb(150, 150, 150)')  # Grey vertical grid lines
    )
    
    fig.update_traces(textposition='outside')  # Display values outside bars

    return fig

def plot_bar_chart2(value1, value2, value3, value4):
    df = pd.DataFrame({
        'unit_type': [
            'High daylight factor', 
            'Medium daylight factor',
            'Low daylight factor',
            'Extremely low daylight factor'
        ],
        'values': [value1, value2, value3, value4]
    })
    
    fig = px.bar(df, y='unit_type', x='values', title="Daylight Factor", 
                 color='unit_type', orientation='h',
                 color_discrete_sequence=['#ea2a00', '#fadd44', '#aecbf7', '#4d6caa'])  # Custom colors
    
    fig.update_layout(
        height = 530,
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
        'unit type': types_list,
        'values': values_list,
    })

    fig = px.pie(df, names='unit type', values='values', hole=0.3,
                 color_discrete_sequence=['#49bf66', '#1c77d9', '#7a36d9', '#c7080b', '#ff8800', '#ffffff'])  # Custom colors
    
    fig.update_layout(
        height = 530,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        paper_bgcolor='rgb(15, 15, 15)',  # Graphite background
        plot_bgcolor='rgb(15, 15, 15)',   # Graphite plot area
        font=dict(color='white'),         # White font color
        title_font=dict(color='white'),   # White title font
        yaxis=dict(showticklabels=False), # Hide y-axis labels
        xaxis=dict(showgrid=True, gridcolor='rgb(150, 150, 150)')  # Grey vertical grid lines
    )
    
    fig.update_traces(textposition='outside', sort = False)  # Display values outside bars

    return fig



# Load Google Sheet
sheet_csv_url = "https://docs.google.com/spreadsheets/d/1Ju7wDVKEIBMoE5DzkIIKqYtXg5rmnVC-52HSGhMYdew/export?format=csv&gid=2078375139"
df = pd.read_csv(sheet_csv_url)
# Apply Styler
styled_df = df.style.set_table_attributes('style="overflow: hidden;"')


pie1 = plot_pie_chart(df['Unit type'].tolist()[:-2], df['Updated quantity (u)'].tolist()[:-2])
pie2 = plot_pie_chart(df['Unit type'].tolist()[:-2], df['Updated Area (m2)'].tolist()[:-2])
pie3 = plot_pie_chart(df['Unit type'].tolist()[:-2], df['Updated Population'].tolist()[:-2])
# pie2.show()


with gr.Blocks() as r_demo:

    with gr.Row(equal_height=True):
            gr.Textbox(value=models_name, label="Last Residential Team Model")
            gr.Textbox(value = version_name(version_unit), label="Last Version")
    with gr.Row(equal_height=True):
            # model_output_1 = gr.Model3D(display_mode='solid', container=False,
            #     clear_color=[0.0, 0.0, 0.0, 0.0], label="UNITS DISTRIBUTION", height=700)
            viewer_iframe = gr.HTML()
            gr.Gallery(value=["images/residential_01.png", "images/residential_02.png", "images/residential_03.jpg"], label="Residential Team Images", 
                        rows=[1], columns=[3], selected_index=0, object_fit="contain", height=750)
            

    gr.Markdown("#", height=50)
    gr.Markdown("# Data", container=True)            
    with gr.Row():
        data = gr.DataFrame(value=df, max_height=10000, column_widths=[50,50,50,50,50,50,50], label="Residential Team Metrics", interactive=False, show_fullscreen_button = True)
    gr.Markdown("#", height=50)
    with gr.Row():
        gr.Markdown("# Statistics", container=True)
    with gr.Row():
        with gr.Column():
            gr.Markdown("## Unit Type Distribution")
            pie1 = gr.Plot(pie1, label="Unit Type Distribution", container=False)
        with gr.Column():
            gr.Markdown("## Area Distribution")
            pie2 = gr.Plot(pie2, label="Area Distribution", container=False)
        with gr.Column():
            gr.Markdown("## Population Distribution")
            pie3 = gr.Plot(pie3, label="Population Distribution", container=False)
    with gr.Row():
        gr.Markdown("#", height=50)


    # gr.Markdown("# KPIs and metrics")
    gr.Markdown("# KPI 1: Views Distribution", container=True)
    with gr.Row(equal_height=True):
        with gr.Column():
            viewer_iframe_views = gr.HTML()
            # model_output_1 = gr.Model3D(display_mode='solid', container=False,
            #     clear_color=[0.0, 0.0, 0.0, 0.0], label="VIEWS DISTRIBUTION", height=700,
            # )
            gr.Image(value="images/residential_view_legend.jpg", show_label=False, container=False,
                     show_fullscreen_button=False, show_download_button=False)
        with gr.Column():
            value1 = gr.Number(label="Best views (%)", value=65, show_label=True)
            value2 = gr.Number(label="Pleasant views (%)", value=15, show_label=True)
            value3 = gr.Number(label="Average views (%)", value=12, show_label=True)
            value4 = gr.Number(label="Worst views (%)", value=8, show_label=True)
            bar_plot1 = gr.Plot(container=False)
    gr.Markdown("#", height=50)
    gr.Markdown("# KPI 2: Solar Analysis", container=True)
    with gr.Row():
        with gr.Column():
            viewer_iframe_solar = gr.HTML()
            # model_output_2 = gr.Model3D(container=False,
            #     clear_color=[0.0, 0.0, 0.0, 0.0], label="SOLAR ANALYSIS", height=700,
            # )
            gr.Image(value="images/residential_solar_legend.jpg", show_label=False, container=False,
                     show_fullscreen_button=False, show_download_button=False)

        with gr.Column():
            value5 = gr.Number(label='High daylight factor (%)', value=67, show_label=True)
            value6 = gr.Number(label='Medium daylight factor (%)', value=22, show_label=True)
            value7 = gr.Number(label='Low daylight factor (%)', value=8, show_label=True)
            value8 = gr.Number(label="Low daylight factor (%)", value=3, show_label=True)
            bar_plot2 = gr.Plot(container=False)

    # Load spekcle viewer
    def initialize_app():
        viewer_url = create_viewer_url(model, version_unit)
        viewer_url_views = create_viewer_url(model_views, version_views)
        viewer_url_solar = create_viewer_url(model_solar, version_solar)
        return viewer_url, viewer_url_views, viewer_url_solar



    r_demo.load(fn=initialize_app, outputs=[viewer_iframe, viewer_iframe_views, viewer_iframe_solar])
    

    # Automatically generate plots
    r_demo.load(plot_bar_chart, inputs=[value1, value2, value3, value4], outputs=bar_plot1)
    r_demo.load(plot_bar_chart2, inputs=[value5, value6, value7, value8], outputs=bar_plot2)
    # r_demo.load(load_mesh, outputs=[model_output_1])

    
# r_demo.launch()

# gradio residential_page.py


    