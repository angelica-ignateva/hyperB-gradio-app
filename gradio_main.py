import gradio as gr
import pandas as pd
import plotly.express as px
from specklepy.api.client import SpeckleClient
from specklepy.api.credentials import get_account_from_token
import matplotlib.pyplot as plt
from structural_page import s_demo
from residential_page import r_demo
from facade_page import f_demo
from industrial_page import i_demo
from service_page import c_demo
from gradio_page import b_demo
# from space_calculator import sc_demo

# Initialize Speckle client and credentials
speckle_server = "macad.speckle.xyz"
speckle_token = "abaa47aed44d2e7faf42d3ba5f7e7440a06b487d9e"
client = SpeckleClient(host=speckle_server)
account = get_account_from_token(speckle_token, speckle_server)
client.authenticate_with_account(account)

# Project ID
# project_id = "daeb18ed0a"
project_id = "28a211b286" # hyperB project


def get_project_data():
    project = client.project.get_with_models(project_id=project_id, models_limit=20)
    return project

def get_all_versions_in_project(project):
    all_versions = []
    project = get_project_data()
    for model in project.models.items:
        versions = client.version.get_versions(model_id=model.id, project_id=project.id, limit=100).items
        all_versions.extend(versions)
    return all_versions

def update_model_selection(project_data):
    models = project_data.models.items
    return gr.Dropdown(choices=[m.name for m in models], label="Select Model")

def version_name(version):
        timestamp = version.createdAt.strftime("%Y-%m-%d %H:%M:%S")
        return ' - '.join([version.authorUser.name, timestamp, version.message])

def update_version_selection(model_name, project_data):
    models = project_data.models.items
    selected_model = [m for m in models if m.name == model_name][0]
    versions = client.version.get_versions(model_id=selected_model.id, project_id=project_data.id, limit=100).items
    
    return gr.Dropdown(choices=[version_name(v) for v in versions], label="Select Version")

def create_viewer_url(model_name, version_key, project_data):
    models = project_data.models.items
    selected_model = [m for m in models if m.name == model_name][0]
    versions = client.version.get_versions(model_id=selected_model.id, project_id=project_data.id, limit=100).items
    keys = [version_name(v) for v in versions]
    selected_version = versions[keys.index(version_key)]
    
    embed_src = f"https://macad.speckle.xyz/projects/{project_data.id}/models/{selected_model.id}@{selected_version.id}#embed=%7B%22isEnabled%22%3Atrue%2C%7D"
    return embed_src

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


def generate_statistics(project_data):
    all_versions = get_all_versions_in_project(project_data)
    
    model_stats_df = generate_model_statistics(project_data)
    connector_stats_df = generate_connector_statistics(all_versions)
    contributor_stats_df = generate_contributor_statistics(all_versions)
    
    return model_stats_df, connector_stats_df, contributor_stats_df

def create_graphs(project_data):
    models = project_data.models.items
    all_versions = get_all_versions_in_project(project_data)
    
    # Model count graph
    model_counts = pd.DataFrame([
        [m.name, len(client.version.get_versions(model_id=m.id, project_id=project_data.id, limit=100).items)]
        for m in models
    ], columns=["modelName", "totalCommits"])
    
    model_graph = px.bar(model_counts, x="modelName", y="totalCommits", 
                        title="Model Commit Distribution")
    model_graph.update_layout(
        paper_bgcolor='rgb(50, 50, 50)',  # Graphite background color
        plot_bgcolor='rgb(50, 50, 50)',   # Graphite background color for the plot area
        font=dict(color='white'),          # Font color for better contrast
        title_font=dict(color='white'))     # Title font color
    
    # Connector distribution
    version_frame = pd.DataFrame.from_dict([{"sourceApplication": v.sourceApplication} for v in all_versions])
    apps = version_frame["sourceApplication"].value_counts().reset_index()
    apps.columns = ["app", "count"]
    connector_graph = px.pie(apps, names="app", values="count", title="Connector Distribution")
    connector_graph.update_layout(
        paper_bgcolor='rgb(50, 50, 50)',  # Background color of the entire chart
        plot_bgcolor='rgb(50, 50, 50)',    # Background color of the plot area
        font=dict(color='white'),          # Font color for better contrast
        title_font=dict(color='white'))
    
    # Contributor distribution
    version_user_names = [v.authorUser.name for v in all_versions]
    authors = pd.DataFrame(version_user_names).value_counts().reset_index()
    authors.columns = ["author", "count"]
    contributor_graph = px.pie(authors, names="author", values="count", title="Contributor Distribution")
    contributor_graph.update_layout(
        paper_bgcolor='rgb(50, 50, 50)',  # Background color of the entire chart
        plot_bgcolor='rgb(50, 50, 50)',    # Background color of the plot area
        font=dict(color='white'),          # Font color for better contrast
        title_font=dict(color='white'))
    
    return model_graph, connector_graph, contributor_graph

def create_timeline(project_data):
    all_versions = get_all_versions_in_project(project_data)
    timestamps = [version.createdAt.date() for version in all_versions]
    timestamps_frame = pd.DataFrame(timestamps, columns=["createdAt"]).value_counts().reset_index()
    timestamps_frame.columns = ["date", "count"]
    timestamps_frame["date"] = pd.to_datetime(timestamps_frame["date"])
    # timeline = px.line(timestamps_frame.sort_values("date"), x="date", y="count", title="Commit Activity Timeline", markers=True)
    return timestamps_frame
    
# Program sheet
SHEET_ID_01 = "1626TKtAEo_EeAreiH9NN3e8-Ju0DRgtV1eINeOqZCoQ"  
EMBED_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID_01}/htmlembed"

# Requirements sheet
sheet_csv_urls = {
    "Residential Team": "https://docs.google.com/spreadsheets/d/1yZRMx0Reso1ye_OGvZoSC9BE_jwYAZAtmm9w8U0fqUs/export?format=csv",
    "Service Team": "https://docs.google.com/spreadsheets/d/1u6Sm7_eCTxN5gY4GMqggZG4zdgEhLy67BjkcpkVXg3A/export?format=csv",
    "Facade Team": "https://docs.google.com/spreadsheets/d/1TbWJKI39oWrXVW4r8LoieRx9nuRdEQvuUVe-rXqotrc/export?format=csv",
    "Structural Team": "https://docs.google.com/spreadsheets/d/1uIBeQa6y3gfS6D8nsHesmj9GVSo7UBWNGTdi6NM4oak/export?format=csv",
    "Industrial Team": "https://docs.google.com/spreadsheets/d/1dxIEr_TIosqf5fb8_GNUxXZuG6WDWhnEfhcFtiDnY_I/export?format=csv",
}

def load_sheet(team):
    if team in sheet_csv_urls:
        df = pd.read_csv(sheet_csv_urls[team])
        return df

# Data for the first pie chart
data_podium = pd.DataFrame({
    "Category": ["Transport & Logistics", "Food Production", "Energy Production", "Parking & Service Areas"],
    "Values": [55710, 24373, 24373, 20891]
})

# Data for the second pie chart
b1 = pd.DataFrame({
    "Category": ["Residential Unit Type 1 (Studio)", "Residential Unit Type 2 (1-Bedroom)", "Amenities", "Residential Green Spaces", 
                 "Circulation & Skywalks","Retail & Shopping"],
    "Values": [72892.94, 90356.87, 121488.23, 60744.12, 107061.50, 18982.54]
})

b2 = pd.DataFrame({
    "Category": ["Residential Unit Type 2 (1-Bedroom)", "Residential Unit Type 3 (2-Bedroom)", "Residential Unit Type 4 (3-Bedroom)", 
                 "Residential Unit Type 5 (4-Bedroom)","Amenities", "Residential Green Spaces", "Circulation & Skywalks", "Retail & Shopping"],
    "Values": [90356.87, 82763.86, 48595.29, 64540.62, 121488.23, 60744.12, 107061.50, 18982.54]
})

b3 = pd.DataFrame({
    "Category": ["Residential Unit Type 3 (2-Bedroom)", "Residential Unit Type 4 (3-Bedroom)", 
                 "Residential Unit Type 5 (4-Bedroom)","Residential Unit Type 6 (Penthouse)", "Amenities", "Residential Green Spaces", "Circulation & Skywalks", "Retail & Shopping"],
    "Values": [82763.86, 48595.29, 64540.62, 17463.93, 121488.23, 60744.12, 107061.50, 18982.54]
})

b4 = pd.DataFrame({
    "Category": ["Olympic Gymnasium", "Co-Working Space", 
                 "Circulation & Skywalks","Retail & Shopping", "Educational Facilities", "Medical, Health & Wellness", "Commercial & Mixed-Use"],
    "Values": [37965.07, 22779.04, 107061.50, 18982.54, 21260.44, 9111.62, 7593.01]
})

df_all = pd.DataFrame({
    "Category": ["Podium", "Building 1", "Building 2", "Building 3", 
                 "Building 4"],
    "Values": [sum(data_podium["Values"]), sum(b1["Values"]), sum(b2["Values"]), sum(b3["Values"]), sum(b4["Values"])]
})

# Create pie charts for program calculator
def create_program_charts():
    # Data for the first pie chart
    fig1, ax1 = plt.subplots(figsize=(8, 8))
    wedges1, _, _ = ax1.pie(data_podium["Values"], autopct='%1.1f%%', 
                            startangle=90, shadow=True, colors=plt.cm.Paired.colors)
    ax1.legend(wedges1, data_podium["Category"], title="Categories", loc='lower right')
    ax1.set_title("Podium", fontsize=16)
    
    fig2, ax2 = plt.subplots(figsize=(8, 8))
    wedges2, _, _ = ax2.pie(b1["Values"], autopct='%1.1f%%', 
                            startangle=90, shadow=True, colors=plt.cm.Paired.colors)
    ax2.legend(wedges2, b1["Category"], title="Categories", loc='lower right')
    ax2.set_title("Building 1", fontsize=16)
    
    fig3, ax3 = plt.subplots(figsize=(8, 8))
    wedges3, _, _ = ax3.pie(b2["Values"], autopct='%1.1f%%', 
                            startangle=90, shadow=True, colors=plt.cm.Paired.colors)
    ax3.legend(wedges3, b2["Category"], title="Categories", loc='lower right')
    ax3.set_title("Building 2", fontsize=16)
    
    fig4, ax4 = plt.subplots(figsize=(8, 8))
    wedges4, _, _ = ax4.pie(b3["Values"], autopct='%1.1f%%', 
                            startangle=90, shadow=True, colors=plt.cm.Paired.colors)
    ax4.legend(wedges4, b3["Category"], title="Categories", loc='lower right')
    ax4.set_title("Building 3", fontsize=16)
    
    fig5, ax5 = plt.subplots(figsize=(8, 8))
    wedges5, _, _ = ax5.pie(b4["Values"], autopct='%1.1f%%', 
                            startangle=90, shadow=True, colors=plt.cm.Paired.colors)
    ax5.legend(wedges5, b4["Category"], title="Categories", loc='lower right')
    ax5.set_title("Building 4", fontsize=16)
    
    fig6, ax6 = plt.subplots(figsize=(8, 8))
    wedges6, _, _ = ax6.pie(df_all["Values"], autopct='%1.1f%%', 
                            startangle=90, shadow=True, colors=plt.cm.Paired.colors)
    ax6.legend(wedges6, df_all["Category"], title="Categories", loc='lower right')
    ax6.set_title("All buildings", fontsize=16)
    
    return fig1, fig2, fig3, fig4, fig5, fig6


# Create the pie charts
fig = px.pie(data_podium, names="Category", values="Values", title="Podium")
fig1 = px.pie(b1, names="Category", values="Values", title="Building 1")
fig2 = px.pie(b2, names="Category", values="Values", title="Building 2")
fig3 = px.pie(b3, names="Category", values="Values", title="Building 3")
fig4 = px.pie(b4, names="Category", values="Values", title="Building 4")
fig5 = px.pie(df_all, names="Category", values="Values", title="All buildings")


# Create Gradio interface
with gr.Blocks(title="Speckle Stream Activity Dashboard") as demo:
    with gr.Tab("Overall Analysis"):
        gr.Markdown("# Speckle Stream Activity Dashboard 📈")
        gr.Markdown("### HyperBuilding B Analytics")
        
        project_data = get_project_data()
        
        with gr.Row():
            model_dropdown = gr.Dropdown(choices=[m.name for m in project_data.models.items], label="Select Model")
            version_dropdown = gr.Dropdown(label="Select Version")
        
        with gr.Row():
            viewer_iframe = gr.HTML(max_height=600)
            model_stats = gr.Dataframe(label="Model Statistics", datatype=["str", "number"], scale = 0.5, show_fullscreen_button=True, show_copy_button=True,
                                    wrap=True, max_height=600)
        
        with gr.Row():
            # model_stats = gr.Dataframe(label="Model Statistics", datatype=["str", "number"])
            connector_stats = gr.Dataframe(label="Connector Statistics", datatype=["str", "number"])
            contributor_stats = gr.Dataframe(label="Contributor Statistics", datatype=["str", "number"])

        
        with gr.Row():
            model_plot = gr.Plot()
            connector_plot = gr.Plot()
            contributor_plot = gr.Plot()
        
        with gr.Row():
            timestamps_frame = create_timeline(project_id)
            timeline_plot = gr.LinePlot(timestamps_frame, x = "date", y = "count")

    with gr.Tab("Program Calculator"):
        gr.Markdown("# Program Calculator")
        gr.HTML(f'<iframe src="{EMBED_URL}" width="100%" height="600px"></iframe>')
        program_charts = create_program_charts()
        with gr.Row():
            gr.Plot(program_charts[0])
            gr.Plot(program_charts[1])
            gr.Plot(program_charts[2])
        with gr.Row():
            gr.Plot(program_charts[3])
            gr.Plot(program_charts[4])
            gr.Plot(program_charts[5])

    # with gr.Tab("Space Calculator"):
    #     sc_demo.render()
    with gr.Tab("Team Requirements"):
        with gr.Row():
            team_dropdown = gr.Dropdown(choices=['Residential Team', 'Facade Team', 'Structural Team', 'Service Team', 'Industrial Team'], 
                                    value="Residential Team",
                                    label='Select Team', 
                                    interactive=True)
        with gr.Row():
            gr.Markdown("# KPI's Team Viewer")
        with gr.Row():
            sheet_display = gr.DataFrame()
            team_dropdown.change(fn=load_sheet, inputs=team_dropdown, outputs=sheet_display)

    with gr.Tab("Structural Team"):
        s_demo.render()
    with gr.Tab("Facade Team"):
        f_demo.render()
    with gr.Tab("Residential Team"):
        r_demo.render()
    with gr.Tab("Industrial Team"):
        i_demo.render()
    with gr.Tab("Service Team"):
        c_demo.render()
    with gr.Tab("Building Analysis"):
        b_demo.render()


    # Load the default team's sheet when the app starts
    demo.load(fn=load_sheet, inputs=team_dropdown, outputs=sheet_display)

    # Initialize statistics and plots once (as State variables)
    model_stats_state = gr.State(generate_statistics(project_data))
    model_plot_state = gr.State(create_graphs(project_data))
    timeline_plot_state = gr.State(create_timeline(project_data))

    # Function to set initial values (this ensures they are displayed)
    def update_static_values():
        return model_stats_state.value + model_plot_state.value + (timeline_plot_state.value,)

    # Call this function at app startup to set fixed statistics and plots
    demo.load(fn=update_static_values, outputs=[
        model_stats, connector_stats, contributor_stats,
        model_plot, connector_plot, contributor_plot,
        timeline_plot
    ])

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


demo.launch()

# gradio gradio_main.py