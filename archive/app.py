import gradio as gr

import gradio_main, space_calculator

with gr.Blocks() as demo:
    gradio_main.demo.render()
with demo.route("Space Calculator"):
    space_calculator.demo.render()

# if __name__ == "__main__":
demo.launch()

# gradio app.py
