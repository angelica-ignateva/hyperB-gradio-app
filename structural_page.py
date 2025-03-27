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
models = [item for item in project.models.items if item.name.startswith('structure/share')]
model = [item for item in project.models.items if item.name.startswith('structure/share/consolidatedmodel')][0]  # Select the first model
models_name = [m.name for m in models]  # Extract model names
model_name = models_name[0]  # Select the first model
versions = client.version.get_versions(model_id=model.id, project_id=project.id, limit=100).items
version = versions[0]  # Select the first version

model_massing = [item for item in project.models.items if item.name.startswith('structure/share/towers/v3/column')][0]
version_massing = client.version.get_versions(model_id=model_massing.id, project_id=project.id, limit=100).items[0]


##################################################

# # Get the referenced object and its dynamic properties
# referenced_obj_id = version.referencedObject
# transport = ServerTransport(project_id, client)
# objData = operations.receive(referenced_obj_id, transport)
# child_obj = objData
# child_obj = child_obj['@Data']['@{0;0;0;0;0;0}'][0]
# names = child_obj.get_dynamic_member_names() # get the attributes on the level object

# obj = {}
# for p in names:
#     obj[p] = child_obj[p]

# data = {"element": [], "volume": []}


# # iterate through and find the elements with a `volume` attribute
# for name in names:
#     prop = child_obj[name]
#     volume = 0
#     volume += prop.volume
#     data["volume"].append(volume)
#     data["element"].append(name[1:]) # removing the prepending `@`

# def generate_graphs(data):
    
#     df = pd.DataFrame(data)
    
#     # Creating figures
#     volumes_fig = px.pie(df, values="volume", names="element", color="element", title="Volumes of Elements (m3)")
#     volumes_fig.update_layout(
#         paper_bgcolor='rgb(50, 50, 50)',  # Graphite background color
#         plot_bgcolor='rgb(50, 50, 50)',
#         height=600,   # Graphite background color for the plot area
#         font=dict(color='white'),          # Font color for better contrast
#         title_font=dict(color='white')     # Title font color
#     )
#     return volumes_fig

# vertices = []

# for p in obj["@glass"].Vertices:
#     vertices.append({"x": p.x, "y": p.y, "z": p.z, "element": "Glass"})

# for x, y, z in np.array(obj["@columns"].vertices).reshape(-1, 3):
#     vertices.append({"x": x, "y": y, "z": z, "element": "Columns"})

# for x, y, z in np.array(obj["@columns"].vertices).reshape(-1, 3):
#     vertices.append({"x": x, "y": y, "z": z, "element": "Main Structure"})

# for x, y, z in np.array(obj["@columns"].vertices).reshape(-1, 3):
#     vertices.append({"x": x, "y": y, "z": z, "element": "Secondary Structure"})


# def generate_scatterplot(vertices):
#     fig = px.scatter_3d(
#     vertices,
#     x="x",
#     y="y",
#     z="z",
#     color="element",
#     opacity=0.7,
#     title="Element Vertices (m)",
#     )
#     fig.update_traces(marker=dict(size=5))  # Adjust 'size' to make dots smaller
#     fig.update_layout(
#         paper_bgcolor='rgb(50, 50, 50)',  # Graphite background color
#         plot_bgcolor='rgb(50, 50, 50)',   # Graphite background color for the plot area
#         font=dict(color='white'),          # Font color for better contrast
#         title_font=dict(color='white'),     # Title font color
#         height=600,
#         legend=dict(
#         x=0,   # Move legend to the left
#         y=1,   # Position it at the top
#         xanchor='left', 
#         yanchor='top',
#         bgcolor='rgba(0,0,0,0)',  # Optional: Transparent background
#         font=dict(color='white')   # Optional: Ensure legend text is visible
#         )
#     )
#     return fig
    
# graphs = generate_graphs(data)
# scatter_plot = generate_scatterplot(vertices)


##################################################

def version_name(model, version):
    timestamp = model.createdAt.strftime("%Y-%m-%d %H:%M:%S")
    return ' - '.join([version.authorUser.name, timestamp, version.message])

def create_viewer_url(model, version):
    embed_src = f"https://macad.speckle.xyz/projects/{project_id}/models/{model.id}@{version.id}#embed=%7B%22isEnabled%22%3Atrue%2C%7D"
    iframe = f'<iframe src="{embed_src}" style="width:100%; height:750px; border:none;"></iframe>'
    return iframe

# Plotting functions
def plot_bar_chart(types_list, values_list):
    df = pd.DataFrame({
        'tower': types_list,
        '% reduction of wind load': values_list,
    })

    fig = px.bar(df, y='tower', x='% reduction of wind load', orientation= 'h', color='tower',
                 color_discrete_sequence=px.colors.sequential.Blues_r)  # or .Viridis, .Inferno, .Magma, etc.
                # color_discrete_sequence=['#49bf66', '#1c77d9', '#7a36d9', '#c7080b', '#ff8800'])  # Custom colors           
    
    fig.update_layout(
        height = 500,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0, font=dict(family="Roboto Mono", size=12, color="white")),
        paper_bgcolor='rgb(15, 15, 15)',  # Graphite background
        plot_bgcolor='rgb(15, 15, 15)',   # Graphite plot area
        font=dict(color='white'),         # White font color
        title_font=dict(color='white'),   # White title font
        yaxis=dict(showticklabels=False), # Hide y-axis labels
        xaxis=dict(showgrid=True, gridcolor='rgb(150, 150, 150)')  # Grey vertical grid lines
    )
    
    fig.update_traces(textposition='outside')  # Display values outside bars

    return fig


##################################################

sheet_csv_url1 = "https://docs.google.com/spreadsheets/d/1Ju7wDVKEIBMoE5DzkIIKqYtXg5rmnVC-52HSGhMYdew/export?format=csv&gid=1574003666"
df1 = pd.read_csv(sheet_csv_url1)
bar1 = plot_bar_chart(df1['Tower number'].tolist(), df1['Reduction, %'].tolist())

def highlight_last_column(s):
    color = 'rgba(24, 100, 181, 0.5)'  # Light blue with 50% transparency
    return [f'background-color: {color}' if s.name == df1.columns[-1] else '' for _ in s]

# Apply the highlighting
styler = df1.style.apply(highlight_last_column, axis=0)


##################################################

# Metrics cards in a row with matching style to your dashboard
metric1_html = """
<div style="padding: 20px; font-family: 'Roboto Mono', monospace;">
    <!-- Import Roboto Mono font -->
    <link href="https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@400;500;700&display=swap" rel="stylesheet">
    
    <h1 style="color: white; margin-bottom: 30px; font-family: 'Roboto Mono', monospace; font-size: 18px;">KPI METRIC</h1>
    
    <div style="display: flex; flex-wrap: wrap; justify-content: space-between; gap: 20px;">
        <!-- Card A -->
        <div style="background-color: #1a1a1a; border-radius: 8px; border-top: 4px solid #1864b5; 
                    flex: 1; min-width: 180px; padding: 24px; box-shadow: 0 0 15px rgba(24, 100, 181, 0.5);">
            <div style="color: #ffffff; font-size: 16px; font-weight: 500; margin-bottom: 12px; letter-spacing: 0.5px; font-family: 'Roboto Mono', monospace;">
                AVERAGE WIND LOAD OPTIMIZATION
            </div>
            <div style="color: #ffffff; font-size: 28px; font-weight: 700; letter-spacing: 0.5px; font-family: 'Roboto Mono', monospace;">
                16.5%
            </div>
        </div>

    </div>
</div>
"""


# GRADIO UI
with gr.Blocks() as st_demo:
    # with gr.Tab(label="Massing structure"):
        gr.Markdown("## Massing Structure Analysis")
        with gr.Row(equal_height=True):
            model_dropdown = gr.Dropdown(choices=models_name, label="Select Industrial Team Model", value = model_name)
            version_text = gr.Textbox(value = version_name(model, version), info="Last version of selected model was sent by ", container=False, lines=2)
        with gr.Row(equal_height=True):
            with gr.Column():
                viewer_iframe = gr.HTML()
            with gr.Column():
                gr.Gallery(value=["structural.png", "structural_00A.png", "structural_00.png"], label="Structural Images", 
                                rows=[1], columns=[3], selected_index=0, object_fit="contain", height=750)
        
        gr.Markdown("#", height=50)
        gr.Markdown("# KPI: Wind Loads", container=True)
        with gr.Row():
            with gr.Column():
                gr.DataFrame(value=styler, label="Wind Loads Metrics", interactive=False, show_fullscreen_button = True, max_height=1000)
                gr.HTML(metric1_html)
            with gr.Column():
                gr.Plot(bar1, container=False, show_label=False)



    # with gr.Tab(label="Podium structure"):
    #     gr.Markdown("## Podium Structure Analysis")
    #     with gr.Row(equal_height=True):
    #         gr.Textbox(value=models_name, label="Last Structural Team Model")
    #         gr.Textbox(value = version_name(), label="Last Version")
    #     with gr.Row(equal_height=True):
    #         with gr.Column():
    #             viewer_iframe = gr.HTML()
    
    #         with gr.Column():
    #             gr.Gallery(value=["images/podium.png", "images/podium.gif"], label="Structural Images", 
    #                     rows=[1], columns=[3], selected_index=0, object_fit="contain", height=600)

    #     with gr.Row():
    #         gr.Plot(value=scatter_plot)
    #         gr.Plot(value=graphs)

        # with gr.Row():
        #     gr.Markdown("## KPIs and metrics")
        # with gr.Row():
        #     with gr.Column():
        #         value1 = gr.Number(label="Standard wind loads (%)", value=100)
        #         value2 = gr.Number(label="Hyper Team B Building wind loads (%)", value=55)
        #         submit_btn1 = gr.Button("Submit")
            
        #     with gr.Column():
        #         value3 = gr.Number(label="Standard bridge load transfer (%)", value=100)
        #         value4 = gr.Number(label="Hyper Team B Building bridge load transfer (%)", value=40)
        #         submit_btn2 = gr.Button("Submit")

                
        # with gr.Row():
        #     with gr.Column():
        #         output1 = gr.Plot()
                
            
        #     with gr.Column():
        #         output2 = gr.Plot()

    


# EVENTS HANDLERS
    # submit_btn1.click(plot_bar_chart, inputs=[value1, value2], outputs=output1)
    # submit_btn2.click(plot_bar_chart2, inputs=[value3, value4], outputs=output2)

    # # Automatically generate the plot when the app loads
    # st_demo.load(plot_bar_chart, inputs=[value1, value2], outputs=output1)
    # st_demo.load(plot_bar_chart2, inputs=[value3, value4], outputs=output2)

        # Load spekcle viewer
        def initialize_app():
            viewer_url = create_viewer_url(model, version)
            return viewer_url


        st_demo.load(fn=initialize_app, outputs=[viewer_iframe])

        def handle_model_change(selected_model_name):
            selected_model = next((m for m in models if m.name == selected_model_name), None)
            if not selected_model:
                return '<p>Model not found</p>'
            version = client.version.get_versions(model_id=selected_model.id, project_id=project.id, limit=5).items[0]
            return create_viewer_url(selected_model, version), version_name(selected_model, version)


        # Event handlers
        model_dropdown.change(fn=handle_model_change, inputs=model_dropdown, outputs=[viewer_iframe, version_text])
    

# st_demo.launch()

# gradio structural_page.py