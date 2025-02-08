import gradio as gr
import pandas as pd
import plotly.express as px
from specklepy.api.client import SpeckleClient
from specklepy.api.credentials import get_account_from_token
import streamlit as st
#import space_calculator

#gradio gradio_main.py

# Initialize Speckle client and credentials
speckle_server = "macad.speckle.xyz"
speckle_token = "abaa47aed44d2e7faf42d3ba5f7e7440a06b487d9e"
client = SpeckleClient(host=speckle_server)
account = get_account_from_token(speckle_token, speckle_server)
client.authenticate_with_account(account)

# Project ID
# project_id = "daeb18ed0a" #kunshaus projects
# project_id = "bf4dedb928" #first project
project_id = "28a211b286" # hyperB project

def get_project_data():
    project = client.project.get_with_models(project_id=project_id, models_limit=20)
    return project

def versions_of_project(project):
    all_versions = []
    for model in project.models.items:
        versions = client.version.get_versions(model_id=model.id, project_id=project.id, limit=100).items
        all_versions.extend(versions)
    return all_versions

def update_model_selection(project_data):
    models = project_data.models.items
    return gr.Dropdown(choices=[m.name for m in models], label="Select Model")

def update_version_selection(model_name, project_data):
    models = project_data.models.items
    selected_model = [m for m in models if m.name == model_name][0]
    versions = client.version.get_versions(model_id=selected_model.id, project_id=project_data.id, limit=100).items
    
    def version_name(version):
        timestamp = version.createdAt.strftime("%Y-%m-%d %H:%M:%S")
        return ' - '.join([version.authorUser.name, timestamp, version.message])
    
    return gr.Dropdown(choices=[version_name(v) for v in versions], label="Select Version")

def create_viewer_url(model_name, version_key, project_data):
    models = project_data.models.items
    selected_model = [m for m in models if m.name == model_name][0]
    versions = client.version.get_versions(model_id=selected_model.id, project_id=project_data.id, limit=100).items
    def version_name(version):
        timestamp = version.createdAt.strftime("%Y-%m-%d %H:%M:%S")
        return ' - '.join([version.authorUser.name, timestamp, version.message])
    keys = [version_name(v) for v in versions]
    selected_version = versions[keys.index(version_key)]
    
    embed_src = f"https://macad.speckle.xyz/projects/{project_data.id}/models/{selected_model.id}@{selected_version.id}#embed=%7B%22isEnabled%22%3Atrue%2C%7D"
    return embed_src

def generate_statistics(project_data):
    all_versions = versions_of_project(project_data)

    def generate_model_statistics(project_data):
        models = project_data.models.items
        data = [{"Model Name": m.name, "Total Commits": len(client.version.get_versions(model_id=m.id, project_id=project_data.id, limit=100).items)} for m in models]
        return pd.DataFrame(data)
    
    def generate_connector_statistics(all_versions):
        connector_list = [v.sourceApplication for v in all_versions]
        df = pd.DataFrame(connector_list, columns=["Connector"])
        df = df["Connector"].value_counts().reset_index()
        df.columns = ["Connector", "Usage Count"]
        return df

    def generate_contributor_statistics(all_versions):
        contributors = [v.authorUser.name for v in all_versions]
        df = pd.DataFrame(contributors, columns=["Contributor"])
        df = df["Contributor"].value_counts().reset_index()
        df.columns = ["Contributor", "Contributions"]
        return df

    
    model_stats_df = generate_model_statistics(project_data)
    connector_stats_df = generate_connector_statistics(all_versions)
    contributor_stats_df = generate_contributor_statistics(all_versions)
    
    return model_stats_df, connector_stats_df, contributor_stats_df


def create_graphs(project_data):
    models = project_data.models.items
    all_versions = versions_of_project(project_data)
    
    # Model count graph
    model_counts = pd.DataFrame([
        [m.name, len(client.version.get_versions(model_id=m.id, project_id=project_data.id, limit=100).items)]
        for m in models
    ], columns=["modelName", "totalCommits"])
    
    model_graph = px.bar(model_counts, x="modelName", y="totalCommits", 
                        title="Model Commit Distribution")
    
    # Connector distribution
    version_frame = pd.DataFrame.from_dict([{"sourceApplication": v.sourceApplication} for v in all_versions])
    apps = version_frame["sourceApplication"].value_counts().reset_index()
    apps.columns = ["app", "count"]
    connector_graph = px.pie(apps, names="app", values="count", title="Connector Distribution")
    
    # Contributor distribution
    version_user_names = [v.authorUser.name for v in all_versions]
    authors = pd.DataFrame(version_user_names).value_counts().reset_index()
    authors.columns = ["author", "count"]
    contributor_graph = px.pie(authors, names="author", values="count", title="Contributor Distribution")
    
    return model_graph, connector_graph, contributor_graph

def create_timeline(project_data):
    all_versions = versions_of_project(project_data)
    timestamps = [version.createdAt.date() for version in all_versions]
    timestamps_frame = pd.DataFrame(timestamps, columns=["createdAt"]).value_counts().reset_index()
    timestamps_frame.columns = ["date", "count"]
    timeline = px.line(timestamps_frame, x="date", y="count", title="Commit Activity Timeline")
    return timeline



# Program sheet
SHEET_ID_01 = "1gO2Rw9J0TRbqERulmcrL8vu8X9flLKgm3qVHrJb6eTA"  
EMBED_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID_01}/htmlembed"

# Requirements sheet
sheet_csv_urls = {
    "Residential Team": "https://docs.google.com/spreadsheets/d/1yZRMx0Reso1ye_OGvZoSC9BE_jwYAZAtmm9w8U0fqUs/export?format=csv",
    "Service Team": "https://docs.google.com/spreadsheets/d/1u6Sm7_eCTxN5gY4GMqggZG4zdgEhLy67BjkcpkVXg3A/export?format=csv",
    "Facade Team": "https://docs.google.com/spreadsheets/d/1TbWJKI39oWrXVW4r8LoieRx9nuRdEQvuUVe-rXqotrc/export?format=csv",
    "Structural Team": "https://docs.google.com/spreadsheets/d/uIBeQa6y3gfS6D8nsHesmj9GVSo7UBWNGTdi6NM4oak/export?format=csv",
    "Industrial Team": "https://docs.google.com/spreadsheets/d/1dxIEr_TIosqf5fb8_GNUxXZuG6WDWhnEfhcFtiDnY_I/export?format=csv",
}

# Function to load the Google Sheet as a DataFrame
def load_sheet(team):
    if team in sheet_csv_urls:
        # Read the CSV data into a DataFrame
        df = pd.read_csv(sheet_csv_urls[team])
        return df




# Create Gradio interface
with gr.Blocks(title="Speckle Stream Activity Dashboard") as demo:
    with gr.Tab("Overall Analysis"):
        gr.Markdown("# Hyper B // Dashboard 📈")
        gr.Markdown("### HyperBuilding B Analytics")
        
        project_data = get_project_data()
        
        with gr.Row():
            model_dropdown = gr.Dropdown(choices=[m.name for m in project_data.models.items], label="Select Model")
            version_dropdown = gr.Dropdown(label="Select Version")
        
        with gr.Row():
                viewer_iframe = gr.HTML(max_height=400)
                model_stats = gr.Dataframe(label="Model Statistics", datatype=["str", "number"], scale=0.5, show_fullscreen_button=True, show_copy_button=True,
                                        wrap=True, max_height=500)
        
        # with gr.Row():
        #     connector_stats = gr.Dataframe(label="Connector Statistics", datatype=["str", "number"])
        #     contributor_stats = gr.Dataframe(label="Contributor Statistics", datatype=["str", "number"])

        
        with gr.Row():
            model_plot = gr.Plot()
            connector_plot = gr.Plot()
            contributor_plot = gr.Plot()
        
        with gr.Row():
            timeline_plot = gr.Plot()

    with gr.Tab("Program Calculator"):
        gr.Markdown("# Program Calculator")
        gr.HTML(f'<iframe src="{EMBED_URL}" width="100%" height="600px"></iframe>')
        

    with gr.Tab("Team Requirements"):
        with gr.Row():
            team_dropdown = gr.Dropdown(choices=['Residential Team', 'Facade Team', 'Structural Team', 'Service Team', 'Industrial Team'], value="Residential Team",
                                        label = 'Select Team', interactive=True)
        with gr.Row():
            gr.Markdown("# KPI's Team Viewer")
        with gr.Row():
            sheet_display = gr.DataFrame()
            team_dropdown.change(fn=load_sheet, inputs=team_dropdown, outputs=sheet_display)

    # Event handlers
    model_dropdown.change(
        fn=lambda x: update_version_selection(x, project_data),
        inputs=model_dropdown,
        outputs=version_dropdown
    )

    
    # Link the dropdown to the display function
    # team_dropdown.change(fn=display_sheet, inputs=team_dropdown, outputs=sheet_display)
    
    def update_viewer_and_stats(model_name, version_key):
        viewer_url = create_viewer_url(model_name, version_key, project_data)
        model_stats_df, connector_stats_df, contributor_stats_df = generate_statistics(project_data)
        model_graph, connector_graph, contributor_graph = create_graphs(project_data)
        timeline = create_timeline(project_data)
    
        return (
            f'<iframe src="{viewer_url}" style="width:100%; height:400px; border:none;"></iframe>',
            model_stats_df, connector_stats_df, contributor_stats_df,
            model_graph, connector_graph, contributor_graph,
            timeline
    )

    
    version_dropdown.change(
        fn=update_viewer_and_stats,
        inputs=[model_dropdown, version_dropdown],
        outputs=[viewer_iframe, model_stats,
                model_plot, connector_plot, contributor_plot, timeline_plot]
    )
    
    # Initialize statistics and graphs
    model_stats.value = generate_statistics(project_data)
    model_plot.value = create_graphs(project_data)
    timeline_plot.value = create_timeline(project_data)

    # Load the default team's sheet when the app starts
    demo.load(fn=load_sheet, inputs=team_dropdown, outputs=sheet_display)

# SPACE CALCULATOR PAGE
# with demo.route("Space calculator"):
#     space_calculator.demo.render()

#if __name__ == "__main__":
demo.launch()

# Streamlit app
# def main():
#     st.title("Streamlit App with Gradio Integration")
    
#     st.write("This app demonstrates how to integrate Gradio with Streamlit using a DataFrame.")
    
#     # Embed the Gradio interface in the Streamlit app
#     st.write("### Gradio Interface")
#     dashboard().launch(share=True, inline=True)

# if __name__ == "__main__":
#     main()