import pandas as pd
import plotly.express as px
import gradio as gr

def plot_bar_chart(value1, value2):
    df = pd.DataFrame({
        'category': ['Standard time', 'Hyper Team B Building time'],
        'values': [value1, value2]
    })
    
    fig = px.bar(df, x='category', y='values', title="Building Contruction time", 
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
        'category': ['Standard construction', 'Hyper Team B Building'],
        'values': [value1, value2]
    })
    custom_colors = ['#1f77b4', '#ff7f0e']  # Blue and orange
    fig = px.bar(df, x='category', y='values', title="Carbon Footprint", 
                 color='category', text='values', color_discrete_sequence=custom_colors)
    
    fig.update_layout(
        paper_bgcolor='rgb(50, 50, 50)',  # Graphite background color
        plot_bgcolor='rgb(50, 50, 50)',   # Graphite background color for the plot area
        font=dict(color='white'),          # Font color for better contrast
        title_font=dict(color='white')     # Title font color
    )

    return fig

with gr.Blocks() as demo:
    with gr.Row():
        with gr.Column():
            value1 = gr.Number(label="Standard time (%)", value=100)
            value2 = gr.Number(label="Hyper Team B Building time (%)", value=55)
            submit_btn1 = gr.Button("Submit")
        
        with gr.Column():
            value3 = gr.Number(label="Standard construction (%)", value=100)
            value4 = gr.Number(label="Hyper Team B Building (%)", value=40)
            submit_btn2 = gr.Button("Submit")

            
    with gr.Row():
        with gr.Column():
            output1 = gr.Plot()
            
        
        with gr.Column():
            output2 = gr.Plot()

    submit_btn1.click(plot_bar_chart, inputs=[value1, value2], outputs=output1)
    submit_btn2.click(plot_bar_chart2, inputs=[value3, value4], outputs=output2)

    # Automatically generate the plot when the app loads
    demo.load(plot_bar_chart, inputs=[value1, value2], outputs=output1)
    demo.load(plot_bar_chart2, inputs=[value3, value4], outputs=output2)

    

demo.launch() # gradio test_page.py