# import gradio as gr
# import pandas as pd
# import plotly.express as px
# from specklepy.api.client import SpeckleClient
# from specklepy.api.credentials import get_account_from_token
# from specklepy.transports.server import ServerTransport
# from specklepy.api import operations
# # import matplotlib.pyplot as plt

# # Project ID
# project_id = "daeb18ed0a"
# model_id = "aab87740df"
# # project_id = "28a211b286" # hyperB project

# # Initialize Speckle client and credentials
# speckle_server = "macad.speckle.xyz"
# speckle_token = "abaa47aed44d2e7faf42d3ba5f7e7440a06b487d9e"
# client = SpeckleClient(host=speckle_server)
# account = get_account_from_token(speckle_token, speckle_server)
# client.authenticate_with_account(account)
# transport = ServerTransport(project_id, client)


# def get_project_data():
#     project = client.project.get_with_models(project_id=project_id, models_limit=20)
#     return project

# def update_model_selection(project_data):
#     models = project_data.models.items
#     return gr.Dropdown(choices=[m.name for m in models], label="Select Model")

# def create_viewer_url(project_data):

#     selected_model = client.model.get(model_id, project_id)
#     versions = client.version.get_versions(model_id=selected_model.id, project_id=project_data.id, limit=100).items
#     selected_version = versions[0]
    
#     embed_src = f"https://macad.speckle.xyz/projects/{project_data.id}/models/{selected_model.id}@{selected_version.id}#embed=%7B%22isEnabled%22%3Atrue%2C%7D"
#     return embed_src

# my_model = client.model.get(model_id, project_id)
# versions = client.version.get_versions(model_id, project_id)
# referenced_obj_id = versions.items[0].referencedObject
# objData = operations.receive(referenced_obj_id, transport)

# child_obj = objData
# dynamic_properties = child_obj.get_dynamic_member_names()

# obj = {}
# for p in dynamic_properties:
#     obj[p] = child_obj[p]


# data = {"element": [], "volume": [], "mass": [], "embodied carbon": []}

# # get the attributes on the level object
# names = child_obj.get_dynamic_member_names()
# # iterate through and find the elements with a `volume` attribute
# for name in names:
#     prop = child_obj[name]
#     for p in prop:
#         volume = 0
#         mass = 0
#         carbon = 0
#         volume += p.volume
#         mass += p.volume * p["@density"]
#         carbon += p.volume * p["@density"] * p["@embodied_carbon"]
#     data["volume"].append(volume)
#     data["mass"].append(mass)
#     data["embodied carbon"].append(carbon)
#     data["element"].append(name[1:]) # removing the prepending `@`


# def generate_graphs(data):
    
#     df = pd.DataFrame(data)
    
#     # Creating figures
#     volumes_fig = px.pie(df, values="volume", names="element", color="element", title="Volumes of Elements (m3)")
#     volumes_fig.update_layout(
#         paper_bgcolor='rgb(50, 50, 50)',  # Graphite background color
#         plot_bgcolor='rgb(50, 50, 50)',   # Graphite background color for the plot area
#         font=dict(color='white'),          # Font color for better contrast
#         title_font=dict(color='white')     # Title font color
#     )

#     carbon_bar_fig = px.bar(df, x="element", y="embodied carbon", color="element", title="Embodied Carbon by Element (kgC02)")
#     carbon_bar_fig.update_layout(
#         paper_bgcolor='rgb(50, 50, 50)',  # Graphite background color
#         plot_bgcolor='rgb(50, 50, 50)',   # Graphite background color for the plot area
#         font=dict(color='white'),          # Font color for better contrast
#         title_font=dict(color='white')     # Title font color
#     )
#     carbon_pie_fig = px.pie(df, values="embodied carbon", names="element", color="element", title="Embodied Carbon by Element (kgC02)")
#     carbon_pie_fig.update_layout(
#         paper_bgcolor='rgb(50, 50, 50)',  # Graphite background color
#         plot_bgcolor='rgb(50, 50, 50)',   # Graphite background color for the plot area
#         font=dict(color='white'),          # Font color for better contrast
#         title_font=dict(color='white')     # Title font color
#     )
#     return volumes_fig, carbon_bar_fig, carbon_pie_fig

# vertices = []

# for element in obj["@Facade"]:
#     for p in element.Vertices:
#         vertices.append({"x": p.x, "y": p.y, "z": p.z, "element": "Facade"})
# for element in obj["@Floors"]:
#     for p in element.Vertices:
#         vertices.append({"x": p.x, "y": p.y, "z": p.z, "element": "Floors"})
# for element in obj["@Walls"]:
#     for p in element.Vertices:
#         vertices.append({"x": p.x, "y": p.y, "z": p.z, "element": "Walls"})
# for element in obj["@Stairs"]:
#     for p in element.Vertices:
#         vertices.append({"x": p.x, "y": p.y, "z": p.z, "element": "Stairs"})

# def generate_scatterplot(vertices):
#     fig = px.scatter_3d(
#     vertices,
#     x="x",
#     y="y",
#     z="z",
#     color="element",
#     opacity=0.7,
#     title="Element Vertices (m)",
# )
#     fig.update_layout(
#         paper_bgcolor='rgb(50, 50, 50)',  # Graphite background color
#         plot_bgcolor='rgb(50, 50, 50)',   # Graphite background color for the plot area
#         font=dict(color='white'),          # Font color for better contrast
#         title_font=dict(color='white'),     # Title font color
#         height=1000,
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

# # Create Gradio interface
# with gr.Blocks(title="Building Analysis", fill_width=True) as b_demo:
#     gr.Markdown("# Building Analysis Dashboard 📈")
#     gr.Markdown("### HyperBuilding B Analytics")
    
#     project_data = get_project_data()
#     model_name="Kunshaus Zurich"
    
#     with gr.Row():
#         model_dropdown = gr.Dropdown(choices=[m.name for m in project_data.models.items], label="Select Model", value = "Kunshaus Zurich", allow_custom_value=True)
#     with gr.Row(equal_height=True):
#         viewer_iframe = gr.HTML()
        

    
#     with gr.Row():
#             gr.Plot(value=graphs[0])
#             gr.Plot(value=graphs[2])
#     gr.Plot(value=graphs[1])
#     with gr.Row():
#         gr.Plot(value=scatter_plot)
    

#     # Event handlers

#     # Load the first model, first version, and version details when the app starts
#     def initialize_app():
#         viewer_url = create_viewer_url(project_data)
#         return f'<iframe src="{viewer_url}" style="width:100%; height:900px; border:none;"></iframe>'


#     b_demo.load(
#         fn=initialize_app,
#         outputs=[viewer_iframe]
# )

# # model_dropdown.change(
# #     fn=lambda x: update_version_selection(x, project_data),
# #     inputs=model_dropdown,
# # )

# def update_viewer_and_stats():
#     viewer_url = create_viewer_url(project_data)
#     return f'<iframe src="{viewer_url}" style="width:100%; height:900px; border:none;"></iframe>'


# b_demo.launch()

# # # gradio gradio_page.py

