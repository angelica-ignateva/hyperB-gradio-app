import gradio as gr
import pandas as pd


data = {
        "Name": ["Alice", "Bob", "Charlie"],
        "Age": [25, 30, 35],
        "City": ["New York", "Los Angeles", "Chicago"]
}
df = pd.DataFrame(data)

with gr.Blocks() as demo:
    gr.Markdown("## DataFrame Display in Gradio")
    dataframe = gr.Dataframe(value=df, interactive=False)

demo.launch()

