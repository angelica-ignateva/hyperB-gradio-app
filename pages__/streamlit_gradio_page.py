# This code combining Streamlit and Gradio finally worked
# To run it, use:
# py -m streamlit run streamlit_page.py

import streamlit as st
import subprocess
# Start Gradio app
aaa = subprocess.Popen(["gradio", "gradio_main.py"])

# Streamlit UI
st.set_page_config(layout="wide")  # Expands Streamlit layout
st.title("Streamlit App with Gradio Integration")

# Gradio interface URL
gradio_interface_url = "http://127.0.0.1:7860/"  # Replace with actual URL if needed

# Center the iframe with CSS
st.markdown(
    """
    <style>
        .centered-frame {
            display: flex;
            justify-content: center;
            align-items: center;
            height: 85vh; 
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# Display centered iframe
st.markdown(
    f"""
    <div class="centered-frame">
        <iframe src="{gradio_interface_url}" width="1600" height="800" style="border:none;"></iframe>
    </div>
    """,
    unsafe_allow_html=True,
)
