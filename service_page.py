import gradio as gr
from specklepy.api.client import SpeckleClient
from specklepy.api.credentials import get_account_from_token
import pandas as pd
import plotly.express as px

# Initialize Speckle client and credentials
speckle_server = "macad.speckle.xyz"
speckle_token = "abaa47aed44d2e7faf42d3ba5f7e7440a06b487d9e"
client = SpeckleClient(host=speckle_server)
account = get_account_from_token(speckle_token, speckle_server)
client.authenticate_with_account(account)

# Project ID
project_id = "28a211b286"

def get_project_data():
    project = client.project.get_with_models(project_id=project_id, models_limit=20)
    return project

# Initialize project data
project_data = get_project_data()

# Filter models whose names start with 'data'
models = [m for m in project_data.models.items if m.name.startswith('service')]
models_name = [m.name for m in models]  # Extract model names
print(models_name)

def version_name(version):
    timestamp = version.createdAt.strftime("%Y-%m-%d %H:%M:%S")
    return ' - '.join([version.authorUser.name, timestamp, version.message])

def update_version_selection(model_name, project_data):
    selected_model = [m for m in models if m.name == model_name][0]
    versions = client.version.get_versions(model_id=selected_model.id, project_id=project_data.id, limit=100).items
    return gr.Dropdown(choices=[version_name(v) for v in versions], label="Select Version")

def create_viewer_url(model_name, version_key, project_data):
    selected_model = [m for m in models if m.name == model_name][0]
    versions = client.version.get_versions(model_id=selected_model.id, project_id=project_data.id, limit=100).items
    keys = [version_name(v) for v in versions]
    selected_version = versions[keys.index(version_key)]
    embed_src = f"https://macad.speckle.xyz/projects/{project_data.id}/models/{selected_model.id}@{selected_version.id}#embed=%7B%22isEnabled%22%3Atrue%2C%7D"
    return embed_src

def get_version_details(project_data):
    all_version_details = []
    
    for model in models:
        versions = client.version.get_versions(model_id=model.id, project_id=project_data.id, limit=100).items
        
        for version in versions:
            all_version_details.append({
                "Model Name": model.name,
                "Timestamp": version.createdAt.strftime("%Y-%m-%d %H:%M:%S"),
                "Author Name": version.authorUser.name,
                "Version Message": version.message
            })
    
    return pd.DataFrame(all_version_details)

def load_default_model_and_version(project_data):
    # Get the first model and its first version
    if not models:
        raise gr.Error("No models found starting with 'structure'.")
    
    first_model = models[0].name
    versions = client.version.get_versions(model_id=models[0].id, project_id=project_data.id, limit=100).items
    if not versions:
        raise gr.Error(f"No versions found for model: {first_model}")
    
    first_version = version_name(versions[0])
    
    # Get the viewer URL and version details DataFrame
    viewer_url = create_viewer_url(first_model, first_version, project_data)
    version_details = get_version_details(project_data)
    
    return first_model, first_version, viewer_url, version_details

first_model, first_version, viewer_url, version_details = load_default_model_and_version(project_data)

print(len(version_details))

def plot_bar_chart(value1, value2):
    df = pd.DataFrame({
        'category': ['Maintenance costs', 'Residents maintenance savings'],
        'values': [value1, value2]
    })
    
    fig = px.bar(df, x='category', y='values', title="Residents savings", 
                 color='category', text='values')
    
    fig.update_layout(
        paper_bgcolor='rgb(50, 50, 50)',  # Graphite background color
        plot_bgcolor='rgb(50, 50, 50)',   # Graphite background color for the plot area
        font=dict(color='white'),          # Font color for better contrast
        title_font=dict(color='white')     # Title font color
    )

    return fig

def plot_bar_chart2(value1, value2):
    df = pd.DataFrame({
        'category': ['Standard system downtime', 'Hyper Team B Building system downtime'],
        'values': [value1, value2]
    })
    custom_colors = ['#1f77b4', '#ff7f0e']  # Blue and orange
    fig = px.bar(df, x='category', y='values', title="System downtime", 
                 color='category', text='values', color_discrete_sequence=custom_colors)
    
    fig.update_layout(
        paper_bgcolor='rgb(50, 50, 50)',  # Graphite background color
        plot_bgcolor='rgb(50, 50, 50)',   # Graphite background color for the plot area
        font=dict(color='white'),          # Font color for better contrast
        title_font=dict(color='white')     # Title font color
    )

    return fig




with gr.Blocks() as c_demo:
    with gr.Row():
        model_dropdown = gr.Dropdown(choices=models_name, label="Select Service Team Model")
        version_dropdown = gr.Dropdown(label="Select Version", allow_custom_value=True)
    
    with gr.Row():
        viewer_iframe = gr.HTML(max_height=600)
        version_details_df = gr.Dataframe(
            label="Version Details",
            headers=["Timestamp", "Author Name", "Version Message"],
            datatype=["str", "str", "str"],
            show_fullscreen_button=True,
            show_copy_button=True,
            wrap=True,
            max_height=600
        )
    with gr.Row():
        gr.Markdown("## KPIs and metrics")
        
    with gr.Row():
        with gr.Column():
            value1 = gr.Number(label="Maintenance costs (%)", value=100)
            value2 = gr.Number(label="Residents maintenance savings (%)", value=55)
            submit_btn1 = gr.Button("Submit")
        
        with gr.Column():
            value3 = gr.Number(label="Standard system downtime (%)", value=100)
            value4 = gr.Number(label="Hyper Team B Building system downtime (%)", value=40)
            submit_btn2 = gr.Button("Submit")

            
    with gr.Row():
        with gr.Column():
            output1 = gr.Plot()
            
        
        with gr.Column():
            output2 = gr.Plot()

    submit_btn1.click(plot_bar_chart, inputs=[value1, value2], outputs=output1)
    submit_btn2.click(plot_bar_chart2, inputs=[value3, value4], outputs=output2)

    # Automatically generate the plot when the app loads
    c_demo.load(plot_bar_chart, inputs=[value1, value2], outputs=output1)
    c_demo.load(plot_bar_chart2, inputs=[value3, value4], outputs=output2)

    # Load the first model, first version, and version details when the app starts
    def initialize_app():
        first_model, first_version, viewer_url, version_details = load_default_model_and_version(project_data)
        return first_model, first_version, f'<iframe src="{viewer_url}" style="width:100%; height:600px; border:none;"></iframe>', version_details


    c_demo.load(
        fn=initialize_app,
        outputs=[model_dropdown, version_dropdown, viewer_iframe, version_details_df]
    )
    

    # Event handlers
    model_dropdown.change(
        fn=lambda x: update_version_selection(x, project_data),
        inputs=model_dropdown,
        outputs=version_dropdown
    )
    
    def update_viewer_and_stats(model_name, version_key):
        viewer_url = create_viewer_url(model_name, version_key, project_data)
        return f'<iframe src="{viewer_url}" style="width:100%; height:600px; border:none;"></iframe>'

    version_dropdown.change(
        fn=update_viewer_and_stats,
        inputs=[model_dropdown, version_dropdown],
        outputs=[viewer_iframe]
    )

# c_demo.launch()

# gradio service_page.py


    