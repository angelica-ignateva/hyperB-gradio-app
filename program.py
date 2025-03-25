import gradio as gr
import pandas as pd
import plotly.express as px
from specklepy.api.client import SpeckleClient
from specklepy.api.credentials import get_account_from_token
# import matplotlib.pyplot as plt
# from structural_page import s_p_demo
# from residential_page import r_p_demo
# from facade_page import f_p_demo
# from industrial_page import i_p_demo
# from service_page import c_p_demo

# from gradio_page import b_p_demo
# from space_calculator import sc_p_demo

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
    project = client.project.get_with_models(project_id=project_id, models_limit=120)
    return project

def get_all_versions_in_project(project):
    all_versions = []
    project = get_project_data()
    for model in project.models.items:
        versions = client.version.get_versions(model_id=model.id, project_id=project.id, limit=120).items
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
    versions = client.version.get_versions(model_id=selected_model.id, project_id=project_data.id, limit=120).items

    return gr.Dropdown(choices=[version_name(v) for v in versions], label="Select Version")

def create_viewer_url(model_name, version_key, project_data):
    models = project_data.models.items
    selected_model = [m for m in models if m.name == model_name][0]
    versions = client.version.get_versions(model_id=selected_model.id, project_id=project_data.id, limit=120).items
    keys = [version_name(v) for v in versions]
    selected_version = versions[keys.index(version_key)]

    embed_src = f"https://macad.speckle.xyz/projects/{project_data.id}/models/{selected_model.id}@{selected_version.id}#embed=%7B%22isEnabled%22%3Atrue%2C%7D"
    return embed_src

def generate_model_statistics(project_data):
    models = project_data.models.items
    data = [{"Model Name": m.name, "Total Commits": len(client.version.get_versions(model_id=m.id, project_id=project_data.id, limit=120).items)} for m in models]
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

    
    
    # Extract models and their commit counts
    model_counts = pd.DataFrame([
        [m.name, len(client.version.get_versions(model_id=m.id, project_id=project_data.id, limit=120).items)]
        for m in models
    ], columns=["modelName", "totalCommits"])

    # Define function to categorize models
    def categorize_model(name):
        if name.startswith("residential"):
            return "Residential"
        elif name.startswith("facade"):
            return "Facade"
        elif name.startswith("structure"):
            return "Structure"
        elif name.startswith("service"):
            return "Service"
        elif name.startswith("industrial"):
            return "Industrial"
        else:
            return "Other"

    # Apply categorization
    model_counts["category"] = model_counts["modelName"].apply(categorize_model)

    # Create bar plot grouped by category
    model_graph = px.bar(
        model_counts, 
        x="modelName", 
        y="totalCommits", 
        color="category",  # Grouped by category
        color_discrete_map={
            "Residential": "green",
            "Facade": "purple",
            "Structure": "blue",
            "Service": "orange",
            "Industrial": "red",
            "Other": "gray"
        }
    )

    # Update layout for dark mode
    model_graph.update_layout(
        height=500,
        legend=dict(orientation="h", yanchor="bottom", y=-0.4, xanchor="center", x=0),
        paper_bgcolor='rgb(15, 15, 15)',
        plot_bgcolor='rgb(15, 15, 15)',
        font=dict(color='white'),
        title_font=dict(color='white')
    )
    
    # Connector distribution
    version_frame = pd.DataFrame.from_dict([{"sourceApplication": v.sourceApplication} for v in all_versions])
    apps = version_frame["sourceApplication"].value_counts().reset_index()
    apps.columns = ["app", "count"]
    connector_graph = px.pie(apps, names="app", values="count", hole=0.4, color_discrete_sequence=px.colors.sequential.Emrld)
    connector_graph.update_layout(
        height = 500,
        legend=dict(orientation="h", yanchor="bottom", y=-0.4, xanchor="center", x=0),
        paper_bgcolor='rgb(15, 15, 15)',  # Background color of the entire chart
        plot_bgcolor='rgb(15, 15, 15)',    # Background color of the plot area
        font=dict(color='white'),          # Font color for better contrast
        title_font=dict(color='white'))
    connector_graph.update_traces(textposition='outside', sort = False, pull=[0.1] * len(apps))  # Display values outside bars
    
    # Contributor distribution
    version_user_names = [v.authorUser.name for v in all_versions]
    authors = pd.DataFrame(version_user_names).value_counts().reset_index()
    authors.columns = ["author", "count"]
    contributor_graph = px.pie(authors, names="author", values="count", hole=0.4, color_discrete_sequence=px.colors.sequential.Sunsetdark)
    contributor_graph.update_layout(
        height = 500,
        legend=dict(orientation="h", yanchor="bottom", y=-0.4, xanchor="center", x=0),
        paper_bgcolor='rgb(15, 15, 15)',  # Background color of the entire chart
        plot_bgcolor='rgb(15, 15, 15)',    # Background color of the plot area
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
    "Values": [55712, 24373, 24373, 20891],
    "Sub-Category": ["Service", "Industrial", "Industrial", "Service"],
})

# Data for the second pie chart
b1 = pd.DataFrame({
    "Category": ["Studio", "1-Bedroom", "Circulation", "Amenities", "Retail", "Green Spaces"],
    "Values": [72892.94, 90356.87, 127061.15, 121488.23, 60744.12, 18982.54],
    "Sub-Category": ["Residential", "Residential","Residential", "Services", "Services", "Services"],
})

b2 = pd.DataFrame({
    "Category": ["1-Bedroom", "2-Bedroom", "3-Bedroom", "Circulation",
                 "4-Bedroom","Amenities", "Green Spaces", "Retail"],
    "Values": [90356.87, 82763.86, 48595.29, 64540.62, 121488.23, 60744.12, 127061.15, 18982.54],
    "Sub-Category": ["Residential", "Residential", "Residential", "Residential",
                 "Residential","Services", "Services", "Services"],
})

b3 = pd.DataFrame({
    "Category": ["2-Bedroom", "3-Bedroom", 
                 "4-Bedroom","Penthouse", "Circulation", "Amenities", "Green Spaces",  "Retail"],
    "Values": [82763.86, 48595.29, 64540.62, 17463.93, 121488.23, 60744.12, 127061.15, 18982.54],
    "Sub-Category": ["Residential", "Residential", 
                 "Residential","Residential", "Residential", "Services", "Services", "Services"],
})

b4 = pd.DataFrame({
    "Category": ["Olympic Gymnasium", "Co-Working Space", 
                 "Circulation","Retail", "Education", "Hospital & Wellness", "Commercial & Mixed-Use"],
    "Values": [37965.07, 22779.04, 127061.15, 18982.54, 212614, 9111.62, 7593.01],
    "Sub-Category": ["Services", "Services", 
                 "Services","Services", "Services", "Services", "Services"]
})

df_all = pd.DataFrame({
    "Category": ["Podium", "Tower 1", "Tower 2", "Tower 3", 
                 "Tower 4"],
    "Values": [sum(data_podium["Values"]), sum(b1["Values"]), sum(b2["Values"]), sum(b3["Values"]), sum(b4["Values"])]
})

def create_piechart(values, names, categories):
    # Define color palettes
    color_palettes = {
        'Residential': px.colors.sequential.Emrld[1:],  
        'Industrial': px.colors.sequential.Reds_r[0:],
        'Services': px.colors.sequential.Oranges[0:]
    }
    
    # Convert categories to a list if it's a Pandas Series
    if isinstance(categories, pd.Series):
        categories = categories.tolist()

    # Assign colors based on category
    color_sequence = []
    for i, cat in enumerate(categories):
        cat = str(cat).strip()  # Remove spaces
        cat = cat.capitalize()  # Ensure proper capitalization (matches keys)

        palette = color_palettes.get(cat, px.colors.sequential.Sunsetdark[3:])  # Default fallback

        if not palette:  # Fallback to gray if empty
            color_sequence.append("#CCCCCC")
        else:
            color_index = i % len(palette)
            color_sequence.append(palette[color_index])

    # Create pie chart
    graph = px.pie(values=values, names=names, hole=0.3, color_discrete_sequence=color_sequence)

    # Style adjustments
    graph.update_layout(
        height=500,
        legend=dict(orientation="h", yanchor="bottom", y=-0.25, xanchor="left", x=0),
        paper_bgcolor='rgb(15, 15, 15)',
        plot_bgcolor='rgb(15, 15, 15)',
        font=dict(color='white'),
        title_font=dict(color='white')
    )

    graph.update_traces(textposition='outside', sort = False)  # Display values outside bars
    
    return graph


# Create the pie charts
fig = px.pie(data_podium, names="Category", values="Values", hole=0.4, color_discrete_sequence=px.colors.sequential.Emrld)
fig.update_layout(height = 500,legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5, font=dict(family="Roboto Mono", size=10, color="white")),
        paper_bgcolor='rgb(15, 15, 15)',  # Graphite background
        plot_bgcolor='rgb(15, 15, 15)',   # Graphite plot area
        font=dict(color='white'),         # White font color
        title_font=dict(color='white'),   # White title font
        yaxis=dict(showticklabels=False), # Hide y-axis labels
        xaxis=dict(showgrid=True, gridcolor='rgb(115, 115, 115)'))
fig.update_traces(textposition='outside', sort = False, pull=[0.1] * len(data_podium))  # Display values outside bars

# fig1 = px.pie(b1, names="Category", values="Values", hole=0.4, color_discrete_sequence=px.colors.sequential.Sunsetdark)
# fig1.update_layout(height = 500,legend=dict(orientation="h", yanchor="bottom", y=-0.4, xanchor="center", x=0.5, font=dict(family="Roboto Mono", size=12, color="white")),
#         paper_bgcolor='rgb(15, 15, 15)',  # Graphite background
#         plot_bgcolor='rgb(15, 15, 15)',   # Graphite plot area
#         font=dict(color='white'),         # White font color
#         title_font=dict(color='white'),   # White title font
#         yaxis=dict(showticklabels=False), # Hide y-axis labels
#         xaxis=dict(showgrid=True, gridcolor='rgb(115, 115, 115)'))
# fig1.update_traces(textposition='outside', sort = False, pull=[0.1] * len(b1))  # Display values outside bars

# fig2 = px.pie(b2, names="Category", values="Values", hole=0.4, color_discrete_sequence=px.colors.sequential.Sunsetdark)
# fig2.update_layout(height = 500,legend=dict(orientation="h", yanchor="bottom", y=-0.4, xanchor="center", x=0.5, font=dict(family="Roboto Mono", size=12, color="white")),
#         paper_bgcolor='rgb(15, 15, 15)',  # Graphite background
#         plot_bgcolor='rgb(15, 15, 15)',   # Graphite plot area
#         font=dict(color='white'),         # White font color
#         title_font=dict(color='white'),   # White title font
#         yaxis=dict(showticklabels=False), # Hide y-axis labels
#         xaxis=dict(showgrid=True, gridcolor='rgb(115, 115, 115)'))
# fig2.update_traces(textposition='outside', sort = False, pull=[0.1] * len(b2))  # Display values outside bars

# fig3 = px.pie(b3, names="Category", values="Values", hole=0.4, color_discrete_sequence=px.colors.sequential.Sunsetdark)
# fig3.update_layout(height = 500,legend=dict(orientation="h", yanchor="bottom", y=-0.4, xanchor="center", x=0.5, font=dict(family="Roboto Mono", size=12, color="white")),
#         paper_bgcolor='rgb(15, 15, 15)',  # Graphite background
#         plot_bgcolor='rgb(15, 15, 15)',   # Graphite plot area
#         font=dict(color='white'),         # White font color
#         title_font=dict(color='white'),   # White title font
#         yaxis=dict(showticklabels=False), # Hide y-axis labels
#         xaxis=dict(showgrid=True, gridcolor='rgb(115, 115, 115)'))
# fig3.update_traces(textposition='outside', sort = False, pull=[0.1] * len(b3))  # Display values outside bars

# fig4 = px.pie(b4, names="Category", values="Values", hole=0.4, color_discrete_sequence=px.colors.sequential.Sunsetdark)
# fig4.update_layout(height = 550,legend=dict(orientation="h", yanchor="bottom", y=-0.4, xanchor="center", x=0.5, font=dict(family="Roboto Mono", size=12, color="white")),
#         paper_bgcolor='rgb(15, 15, 15)',  # Graphite background
#         plot_bgcolor='rgb(15, 15, 15)',   # Graphite plot area
#         font=dict(color='white'),         # White font color
#         title_font=dict(color='white'),   # White title font
#         yaxis=dict(showticklabels=False), # Hide y-axis labels
#         xaxis=dict(showgrid=True, gridcolor='rgb(115, 115, 115)'))
# fig4.update_traces(textposition='outside', sort = False, pull=[0.1] * len(b4))  # Display values outside bars

fig5 = px.pie(df_all, names="Category", values="Values", hole=0.4, color_discrete_sequence=px.colors.sequential.Agsunset_r)
fig5.update_layout(height = 500, legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5, font=dict(family="Roboto Mono", size=10, color="white")),
        paper_bgcolor='rgb(15, 15, 15)',  # Graphite background
        plot_bgcolor='rgb(15, 15, 15)',   # Graphite plot area
        font=dict(color='white'),         # White font color
        title_font=dict(color='white'),   # White title font
        yaxis=dict(showticklabels=False), # Hide y-axis labels
        xaxis=dict(showgrid=True, gridcolor='rgb(115, 115, 115)'))
fig5.update_traces(textposition='outside', sort = False, pull=[0.1] * len(df_all))  # Display values outside bars

fig1 = create_piechart(b1['Values'], b1['Category'], b1['Sub-Category'])
fig2 = create_piechart(b2['Values'], b2['Category'], b2['Sub-Category'])
fig3 = create_piechart(b3['Values'], b3['Category'], b3['Sub-Category'])
fig4 = create_piechart(b4['Values'], b4['Category'], b4['Sub-Category'])
# fig = create_piechart(data_podium['Values'], data_podium['Category'], data_podium['Sub-Category'])

# Create Gradio interface
with gr.Blocks(title="Speckle Stream Activity Dashboard") as p_demo:
        gr.Markdown("#", height=15)
        # gr.Markdown("## Program Distribution 🏢")
        with gr.Row():
                gr.Image(value="hyperB.png", show_label=False, container=False, show_fullscreen_button=False, show_download_button=False, height=800)
        # with gr.Row():
        #             gr.Image(value="images/hyperB_02.jpg", show_label=False, container=False, show_fullscreen_button=False, show_download_button=False, height=400)
        #             gr.Image(value="images/hyperB_03.jpg", show_label=False, container=False, show_fullscreen_button=False, show_download_button=False, height=400)
        #             gr.Image(value="images/hyperB_04.jpg", show_label=False, container=False, show_fullscreen_button=False, show_download_button=False, height=400)
        # # gr.HTML(f'<iframe src="{EMBED_URL}" width="120%" height="500px"></iframe>')
        # # program_charts = create_program_charts()
        gr.Markdown("#", height=50)
        with gr.Row():
            with gr.Column():
                gr.Markdown("### All Towers", container=True) 
                gr.Plot(fig5, container=False, show_label=False)
            with gr.Column():
                gr.Markdown("## Podium - Transport & Industry", container=True) 
                gr.Plot(fig, container=False, show_label=False)
        gr.Markdown("#", height=15)
        with gr.Row():
            
            with gr.Column():
                gr.Markdown("### Tower 1 - Mixed,  GFA - 110k m² ", container=True) 
                gr.Plot(fig1, container=False, show_label=False)
            with gr.Column():
                gr.Markdown("### Tower 2 - Mixed,  GFA - 120k m² ", container=True) 
                gr.Plot(fig2, container=False, show_label=False)
        gr.Markdown("#", height=15)   
        with gr.Row():
                
            with gr.Column():
                gr.Markdown("### Tower 3 - Mixed,  GFA - 115k m² ", container=True) 
                gr.Plot(fig3, container=False, show_label=False)
            with gr.Column():
                gr.Markdown("### Tower 4 - Service,  GFA - 95k m² ", container=True) 
                gr.Plot(fig4, container=False, show_label=False)
            

    # with gr.Tab("Speckle Insights"):
    #     gr.Markdown("# Speckle Stream Activity Dashboard 📈")
    #     gr.Markdown("### HyperBuilding B Analytics")
        
    #     project_data = get_project_data()
        
    #     with gr.Row():
    #         model_dropdown = gr.Dropdown(choices=[m.name for m in project_data.models.items], label="Select Model")
    #         version_dropdown = gr.Dropdown(label="Select Version")
        
    #     with gr.Row():
    #         viewer_iframe = gr.HTML(max_height=500)
    #         model_stats = gr.Dataframe(label="Model Statistics", datatype=["str", "number"], scale = 0.5, show_fullscreen_button=True, show_copy_button=True,
    #                                 wrap=True, max_height=500)
        
    #     with gr.Row():
    #         # model_stats = gr.Dataframe(label="Model Statistics", datatype=["str", "number"])
    #         connector_stats = gr.Dataframe(label="Connector Statistics", datatype=["str", "number"])
    #         contributor_stats = gr.Dataframe(label="Contributor Statistics", datatype=["str", "number"])

        
    #     with gr.Row():
    #         model_plot = gr.Plot(container=False, label="Model Commit Distribution")
            
        
    #     with gr.Row():
    #         timestamps_frame = create_timeline(project_id)
    #         timeline_plot = gr.LinePlot(timestamps_frame, x = "date", y = "count")
    #     with gr.Row():
    #         connector_plot = gr.Plot(container=False, label="Connector Distribution")
    #         contributor_plot = gr.Plot(container=False, label="Contributor Distribution")
            

    # with gr.Tab("Space Calculator"):
    #     sc_p_demo.render()
    # with gr.Tab("Team Requirements"):
    #     with gr.Row():
    #         team_dropdown = gr.Dropdown(choices=['Residential Team', 'Facade Team', 'Structural Team', 'Service Team', 'Industrial Team'], 
    #                                 value="Residential Team",
    #                                 label='Select Team', 
    #                                 interactive=True)
    #     with gr.Row():
    #         gr.Markdown("# KPI's Team Viewer")
    #     with gr.Row():
    #         sheet_display = gr.DataFrame()
    #         team_dropdown.change(fn=load_sheet, inputs=team_dropdown, outputs=sheet_display)
    
    # with gr.Tab("Residential Team"):
    #     r_p_demo.render()

    # with gr.Tab("Service Team"):
    #     c_p_demo.render()

    # with gr.Tab("Industrial Team"):
    #     i_p_demo.render()

    # with gr.Tab("Structural Team"):
    #     s_p_demo.render()
    # with gr.Tab("Facade Team"):
    #     f_p_demo.render()
    
    
    
    # with gr.Tab("Building Analysis"):
    #     b_p_demo.render()


    # # Load the default team's sheet when the app starts
    # p_demo.load(fn=load_sheet, inputs=team_dropdown, outputs=sheet_display)

    # # Initialize statistics and plots once (as State variables)
    # model_stats_state = gr.State(generate_statistics(project_data))
    # model_plot_state = gr.State(create_graphs(project_data))
    # timeline_plot_state = gr.State(create_timeline(project_data))

    # # Function to set initial values (this ensures they are displayed)
    # def update_static_values():
    #     return model_stats_state.value + model_plot_state.value + (timeline_plot_state.value,)

    # # Call this function at app startup to set fixed statistics and plots
    # p_demo.load(fn=update_static_values, outputs=[
    #     model_stats, connector_stats, contributor_stats,
    #     model_plot, connector_plot, contributor_plot,
    #     timeline_plot
    # ])

    # # Event handlers
    # model_dropdown.change(
    #     fn=lambda x: update_version_selection(x, project_data),
    #     inputs=model_dropdown,
    #     outputs=version_dropdown
    # )
    
    # def update_viewer_and_stats(model_name, version_key):
    #     viewer_url = create_viewer_url(model_name, version_key, project_data)
    #     return f'<iframe src="{viewer_url}" style="width:120%; height:500px; border:none;"></iframe>'

    
    # version_dropdown.change(
    #     fn=update_viewer_and_stats,
    #     inputs=[model_dropdown, version_dropdown],
    #     outputs=[viewer_iframe]
    # )


# p_demo.launch()

# gradio program.py