import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
import json
import numpy as np

# Carbon emission factors (kg CO2 per kg of material)
CARBON_EMISSION_FACTORS = {
    'concrete': 0.272,  # kg CO2 per kg of concrete
    'steel': 2.0,       # kg CO2 per kg of steel
    'aluminum': 16.7,   # kg CO2 per kg of aluminum
    'glass': 1.5,       # kg CO2 per kg of glass
    'wood': 0.5,        # kg CO2 per kg of wood
    'brick': 0.185,     # kg CO2 per kg of brick
    'copper': 4.5,      # kg CO2 per kg of copper
    'plastic': 2.5,     # kg CO2 per kg of plastic
}

def load_json_data(uploaded_file):
    """Load and validate JSON data"""
    try:
        data = json.load(uploaded_file)
        df = pd.DataFrame(data)
        
        # Validate required columns
        required_columns = ['category', 'material', 'density', 'volume', 'quantity']
        for col in required_columns:
            if col not in df.columns:
                st.error(f"Missing required column: {col}")
                return None
        
        return df
    except json.JSONDecodeError:
        st.error("Invalid JSON file. Please upload a properly formatted JSON.")
        return None

def calculate_carbon_emissions(df):
    """Calculate carbon emissions for each material"""
    # Calculate mass and carbon emissions
    df['mass'] = df['density'] * df['volume'] * df['quantity']
    
    # Calculate carbon emissions using emission factors
    df['carbon_emissions'] = df.apply(
        lambda row: CARBON_EMISSION_FACTORS.get(row['material'].lower(), 0) * row['mass'], 
        axis=1
    )
    
    return df

def create_emissions_summary(df):
    """Create summary of carbon emissions"""
    emissions_summary = df.groupby('category').agg({
        'carbon_emissions': 'sum',
        'mass': 'sum'
    }).reset_index()
    
    return emissions_summary

def create_pie_chart(emissions_summary):
    """Create pie chart of emissions by category"""
    fig = px.pie(
        emissions_summary, 
        values='carbon_emissions', 
        names='category',
        title='Carbon Emissions by Category',
        hole=0.3
    )
    return fig

def create_bar_plot(emissions_summary):
    """Create bar plot of emissions by category"""
    fig = px.bar(
        emissions_summary, 
        x='category', 
        y='carbon_emissions',
        title='Carbon Emissions Breakdown',
        labels={'category': 'Category', 'carbon_emissions': 'Carbon Emissions (kg CO2)'}
    )
    return fig

def create_material_emissions_plot(df):
    """Create bar plot of emissions by material"""
    material_emissions = df.groupby('material')['carbon_emissions'].sum().reset_index()
    material_emissions = material_emissions.sort_values('carbon_emissions', ascending=False)
    
    fig = px.bar(
        material_emissions, 
        x='material', 
        y='carbon_emissions',
        title='Carbon Emissions by Material',
        labels={'material': 'Material', 'carbon_emissions': 'Carbon Emissions (kg CO2)'}
    )
    return fig

def main():
    st.set_page_config(page_title="Architectural Carbon Emissions Analyzer", layout="wide")
    
    st.title("🏗️ Architectural Carbon Emissions Analysis")
    
    # Sidebar for file upload and emissions factors
    st.sidebar.header("Upload Building Materials Data")
    uploaded_file = st.sidebar.file_uploader(
        "Choose a JSON file", 
        type=['json'],
        help="Upload a JSON file with building materials data"
    )
    
    # Emissions Factors Expander
    with st.sidebar.expander("Carbon Emission Factors"):
        st.write("Current Emission Factors (kg CO2 per kg of material):")
        for material, factor in CARBON_EMISSION_FACTORS.items():
            st.text(f"{material.capitalize()}: {factor}")
    
    if uploaded_file is not None:
        # Load and process data
        df = load_json_data(uploaded_file)
        
        if df is not None:
            # Calculate carbon emissions
            df = calculate_carbon_emissions(df)
            emissions_summary = create_emissions_summary(df)
            
            # Overview Section
            st.header("Emissions Overview")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                total_emissions = df['carbon_emissions'].sum()
                st.metric("Total Carbon Emissions", f"{total_emissions:.2f} kg CO2")
            
            with col2:
                total_mass = df['mass'].sum()
                st.metric("Total Material Mass", f"{total_mass:.2f} kg")
            
            with col3:
                st.metric("Unique Materials", len(df['material'].unique()))
            
            # Visualizations
            st.header("Emissions Visualizations")
            
            # Create columns for charts
            col1, col2 = st.columns(2)
            
            with col1:
                # Pie Chart
                pie_chart = create_pie_chart(emissions_summary)
                st.plotly_chart(pie_chart, use_container_width=True)
            
            with col2:
                # Bar Plot by Category
                bar_plot = create_bar_plot(emissions_summary)
                st.plotly_chart(bar_plot, use_container_width=True)
            
            # Material Emissions Bar Plot
            st.plotly_chart(create_material_emissions_plot(df), use_container_width=True)
            
            # Detailed Data Tables
            st.header("Detailed Analysis")
            
            # Emissions by Category
            st.subheader("Emissions by Category")
            st.dataframe(emissions_summary)
            
            # Raw Materials Data
            st.subheader("Detailed Materials Data")
            st.dataframe(df)
            
            # Download Options
            st.header("Download Analysis")
            col1, col2 = st.columns(2)
            
            with col1:
                csv = df.to_csv(index=False)
                st.download_button(
                    label="Download Detailed Data as CSV",
                    data=csv,
                    file_name="architectural_carbon_emissions.csv",
                    mime="text/csv"
                )
            
            with col2:
                json_data = df.to_json(orient="records")
                st.download_button(
                    label="Download Detailed Data as JSON",
                    data=json_data,
                    file_name="architectural_carbon_emissions.json",
                    mime="application/json"
                )
    
    else:
        # Welcome/Instructions
        st.markdown("""
        ## Architectural Carbon Emissions Analyzer 🏢

        ### How to Use:
        1. Upload a JSON file with building materials data
        2. The tool will automatically generate:
           - Total carbon emissions overview
           - Pie chart of emissions by category
           - Bar plots of emissions by category and material
           - Detailed materials data table
           - Downloadable CSV and JSON files

        ### Expected JSON Format:
        ```json
        [
            {
                "category": "Structure",
                "material": "Concrete",
                "density": 2.4,
                "volume": 50,
                "quantity": 1
            },
            {
                "category": "Facade",
                "material": "Glass",
                "density": 2.5,
                "volume": 20,
                "quantity": 1
            }
        ]
        ```
        """)

        # Sample Data Download
        st.sidebar.header("Sample Data")
        sample_data = [
            {
                "category": "Structure",
                "material": "Concrete",
                "density": 2.4,
                "volume": 50,
                "quantity": 1
            },
            {
                "category": "Facade",
                "material": "Glass",
                "density": 2.5,
                "volume": 20,
                "quantity": 1
            },
            {
                "category": "Roofing",
                "material": "Steel",
                "density": 7.85,
                "volume": 10,
                "quantity": 1
            },
            {
                "category": "Interior",
                "material": "Wood",
                "density": 0.7,
                "volume": 30,
                "quantity": 1
            }
        ]
        
        st.sidebar.download_button(
            label="Download Sample JSON",
            data=json.dumps(sample_data, indent=2),
            file_name="sample_architectural_carbon_emissions.json",
            mime="application/json"
        )

if __name__ == "__main__":
    main()