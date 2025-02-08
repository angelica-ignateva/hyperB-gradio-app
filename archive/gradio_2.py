import gradio as gr
import pandas as pd
import plotly.express as px
from specklepy.api.client import SpeckleClient
from specklepy.api.credentials import get_account_from_token
import importlib.util

def create_dashboard():
    # Initialize Speckle client and credentials
    speckle_server = "macad.speckle.xyz"
    speckle_token = "abaa47aed44d2e7faf42d3ba5f7e7440a06b487d9e"
    client = SpeckleClient(host=speckle_server)
    account = get_account_from_token(speckle_token, speckle_server)
    client.authenticate_with_account(account)
    
    # Project ID
    project_id = "28a211b286" # hyperB project
    
    # Import space_calculator module
    spec = importlib.util.spec_from_file_location("space_calculator", "space_calculator.py")
    space_calculator = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(space_calculator)
    
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
        models = project_data.models.items
        all_versions = versions_of_project(project_data)
        
        # Model statistics
        model_stats = f"Number of Models: {len(models)}\nModel Names:\n" + "\n".join([f"- {m.name}" for m in models])
        
        # Connector statistics
        connector_list = [v.sourceApplication for v in all_versions]
        unique_connectors = list(dict.fromkeys(connector_list))
        connector_stats = f"Number of Connectors: {len(unique_connectors)}\nConnector Names:\n" + "\n".join([f"- {c}" for c in unique_connectors])
        
        # Contributor statistics
        contributors = []
        for version in all_versions:
            contributors.append(version.authorUser.name)
        unique_contributors = list(dict.fromkeys(contributors))
        contributor_stats = f"Number of Contributors: {len(unique_contributors)}\nContributor Names:\n" + "\n".join([f"- {c}" for c in unique_contributors])
        
        return model_stats, connector_stats, contributor_stats
    
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

    # Create Gradio interface with side menu
    with gr.Blocks(title="Speckle Stream Activity Dashboard") as dashboard:
        with gr.Row():
            # Side menu column
            with gr.Column(scale=1):
                gr.Markdown("### Navigation")
                with gr.Tabs() as tabs:
                    with gr.Tab("Overall Project Analytics"):
                        gr.Markdown("") # Placeholder for spacing
                    with gr.Tab("Space Calculator"):
                        gr.Markdown("") # Placeholder for spacing
            
            # Main content column
            with gr.Column(scale=4):
                # Content for Overall Project Analytics tab
                with gr.Tab("Overall Project Analytics", id=0):
                    gr.Markdown("# Speckle Stream Activity Dashboard 📈")
                    gr.Markdown("### HyperBuilding B Analytics")
                    
                    project_data = get_project_data()
                    
                    with gr.Row():
                        model_dropdown = gr.Dropdown(choices=[m.name for m in project_data.models.items], label="Select Model")
                        version_dropdown = gr.Dropdown(label="Select Version")
                    
                    with gr.Row():
                        viewer_iframe = gr.HTML()
                    
                    with gr.Row():
                        model_stats = gr.TextArea(label="Model Statistics")
                        connector_stats = gr.TextArea(label="Connector Statistics")
                        contributor_stats = gr.TextArea(label="Contributor Statistics")
                    
                    with gr.Row():
                        model_plot = gr.Plot()
                        connector_plot = gr.Plot()
                        contributor_plot = gr.Plot()
                    
                    with gr.Row():
                        timeline_plot = gr.Plot()
                
                # Content for Space Calculator tab
                with gr.Tab("Space Calculator", id=1):
                    # Import and create the space calculator interface
                    space_calculator_interface = space_calculator.create_space_calculator()
        
        # Event handlers
        model_dropdown.change(
            fn=lambda x: update_version_selection(x, project_data),
            inputs=model_dropdown,
            outputs=version_dropdown
        )
        
        def update_viewer_and_stats(model_name, version_key):
            viewer_url = create_viewer_url(model_name, version_key, project_data)
            model_stats, connector_stats, contributor_stats = generate_statistics(project_data)
            model_graph, connector_graph, contributor_graph = create_graphs(project_data)
            timeline = create_timeline(project_data)
            return (
                f'<iframe src="{viewer_url}" style="width:100%; height:400px; border:none;"></iframe>',
                model_stats, connector_stats, contributor_stats,
                model_graph, connector_graph, contributor_graph,
                timeline
            )
        
        version_dropdown.change(
            fn=update_viewer_and_stats,
            inputs=[model_dropdown, version_dropdown],
            outputs=[viewer_iframe, model_stats, connector_stats, contributor_stats,
                    model_plot, connector_plot, contributor_plot, timeline_plot]
        )
        
        # Initialize statistics and graphs
        model_stats.value, connector_stats.value, contributor_stats.value = generate_statistics(project_data)
        model_plot.value, connector_plot.value, contributor_plot.value = create_graphs(project_data)
        timeline_plot.value = create_timeline(project_data)
    
    return dashboard

# if __name__ == "__main__":
dashboard = create_dashboard()
dashboard.launch()

#gradio gradio_2.py