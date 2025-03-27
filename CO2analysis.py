import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objs as go
import json
import math

class HyperbuildingCarbonAnalyzer:
    """
    A comprehensive carbon emissions analyzer for hyperbuidings,
    focusing on advanced material carbon footprint calculations.
    """
    def __init__(self):
        """
        Initialize emission factors for various building materials 
        with granular categorization.
        """
        self.EMISSION_FACTORS = {
            # Structural Materials
            'concrete': {
                'base': 0.272,  # Standard concrete
                'high_performance': 0.15,  # Low-carbon concrete
                'ultra_high_performance': 0.1  # Advanced low-carbon concrete
            },
            'steel': {
                'standard': 2.0,  # Conventional steel
                'recycled': 0.5,  # Recycled steel
                'low_carbon': 1.0  # Low-carbon steel production
            },
            'aluminum': {
                'standard': 16.7,  # Primary aluminum
                'recycled': 2.5,   # Recycled aluminum
            },
            
            # Facade Materials
            'glass': {
                'standard': 1.5,   # Standard glass
                'low_e': 1.2,      # Low-emissivity glass
                'smart_glass': 1.0 # Advanced smart glass
            },
            
            # Insulation and Additional Materials
            'insulation': {
                'fiberglass': 0.6,
                'rock_wool': 0.4,
                'aerogel': 0.2
            },
            
            # Specialized Hyperbuilding Materials
            'carbon_fiber': {
                'standard': 8.0,
                'advanced': 5.0
            },
            'advanced_composites': {
                'lightweight': 3.0,
                'ultra_lightweight': 1.5
            }
        }
        
        # Hyperbuilding Specific Components
        self.HYPERBUILDING_COMPONENTS = [
            'vertical_transportation',
            'structural_core',
            'external_facade',
            'internal_systems',
            'sky_gardens',
            'renewable_energy_integration',
            'smart_building_systems'
        ]

    def generate_sample_hyperbuilding_json(self, complexity='medium'):
        """
        Generate sample hyperbuilding JSON with varied complexity.
        
        Args:
            complexity (str): Complexity level of the sample data.
        
        Returns:
            list: Sample hyperbuilding materials data.
        """
        complexity_factors = {
            'low': (0.5, 1),
            'medium': (1, 2),
            'high': (2, 3)
        }
        
        multiplier, variation = complexity_factors.get(complexity, (1, 2))
        
        sample_data = [
            {
                "component": "structural_core",
                "material": "concrete",
                "material_type": "high_performance",
                "density": 2.4,
                "volume": 50 * multiplier,
                "location": "central_core"
            },
            {
                "component": "external_facade",
                "material": "glass",
                "material_type": "low_e",
                "density": 2.5,
                "volume": 30 * multiplier,
                "energy_efficiency_rating": "high"
            },
            {
                "component": "structural_core",
                "material": "steel",
                "material_type": "low_carbon",
                "density": 7.85,
                "volume": 20 * multiplier,
                "recycled_content_percentage": 50
            }
        ]
        
        return sample_data

    def calculate_carbon_emissions(self, data):
        """
        Calculate carbon emissions for hyperbuilding materials.
        
        Args:
            data (list): List of material dictionaries.
        
        Returns:
            list: Detailed carbon emissions data.
        """
        emissions_data = []
        
        for item in data:
            # Validate required keys
            required_keys = ['material', 'material_type', 'density', 'volume']
            if not all(key in item for key in required_keys):
                st.warning(f"Skipping invalid entry: {item}")
                continue
            
            material = item['material']
            material_type = item.get('material_type', 'standard')
            
            try:
                emission_factor = self.EMISSION_FACTORS[material][material_type]
            except KeyError:
                st.warning(f"No emission factor for {material} ({material_type}). Using default.")
                emission_factor = 0.5  # Default conservative estimate
            
            # Calculate mass and carbon emissions
            mass = item['density'] * item['volume']
            carbon_emissions = mass * emission_factor
            
            emissions_data.append({
                **item,
                'mass': mass,
                'emission_factor': emission_factor,
                'carbon_emissions': carbon_emissions
            })
        
        return emissions_data

def main():
    """Main Streamlit application entry point."""
    st.set_page_config(
        page_title="Hyperbuilding Carbon Emissions Analyzer", 
        page_icon="🏙️", 
        layout="wide"
    )
    
    analyzer = HyperbuildingCarbonAnalyzer()
    
    st.title("🏙️ Hyperbuilding Carbon Emissions Analyzer")
    # st.subheader("Advanced Carbon Footprint Assessment for Modern Architecture")
    
    # Sidebar Configuration
    with st.sidebar:
        st.header("Analysis Tools")
        
        st.subheader("Sample Data Generation")
        complexity = st.selectbox(
            "Complexity Level", 
            ["low", "medium", "high"],
            help="Select the complexity of the generated sample data"
        )
        
        if st.button("Generate Sample JSON", help="Create a sample JSON for analysis"):
            sample_data = analyzer.generate_sample_hyperbuilding_json(complexity)
            
            with open("hyperbuilding_sample_data.json", "w") as f:
                json.dump(sample_data, f, indent=2)
            
            st.success("Sample JSON generated and saved!")
        
        st.subheader("Data Upload")
        uploaded_file = st.file_uploader(
            "Upload Materials JSON", 
            type=['json'],
            help="Upload a JSON file containing building material details"
        )
    
    # Main Analysis Section
    if uploaded_file is not None:
        try:
            data = json.load(uploaded_file)
            emissions_data = analyzer.calculate_carbon_emissions(data)
            
            df = pd.DataFrame(emissions_data)
            
            # Overview Metrics
            st.header("Carbon Emissions Overview")
            col1, col2 = st.columns(2, border=True)
            
            with col1:
                total_emissions = df['carbon_emissions'].sum()
                st.metric("Total Carbon Emissions", f"{total_emissions:,.2f} kg CO2")
            
            with col2:
                total_mass = df['mass'].sum()
                st.metric("Total Material Mass", f"{total_mass:,.2f} kg")
            
            # Visualizations
            st.header("Detailed Carbon Analysis")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Emissions by Component Pie Chart
                component_emissions = df.groupby('component')['carbon_emissions'].sum()
                fig_pie = px.pie(
                    height=600,
                    color_discrete_sequence=px.colors.sequential.Sunsetdark,
                    values=component_emissions.values, 
                    names=component_emissions.index,
                    title='Carbon Emissions by Building Component',
                    hole=0.3
                )
                st.plotly_chart(fig_pie, use_container_width=True)
            
            with col2:
                # Emissions by Material Bar Chart
                material_emissions = df.groupby('material')['carbon_emissions'].sum()
                fig_bar = px.bar(
                    height=600,
                    color_discrete_sequence=px.colors.sequential.Emrld_r,
                    x=material_emissions.index, 
                    y=material_emissions.values,
                    color=material_emissions.index,
                    title='Carbon Emissions by Material',
                    labels={'x': 'Material', 'y': 'Carbon Emissions (kg CO2)'}
                )
                st.plotly_chart(fig_bar, use_container_width=True)
            
            # Detailed Data Table
            st.header("Comprehensive Emissions Data")
            st.dataframe(df, use_container_width=True, height=1000)
            
            # Download Options
            st.header("Export Analysis")
            col1, col2 = st.columns(2)
            
            with col1:
                st.download_button(
                    label="Download CSV Report",
                    data=df.to_csv(index=False),
                    file_name="hyperbuilding_carbon_emissions.csv",
                    mime="text/csv"
                )
            
            with col2:
                st.download_button(
                    label="Download JSON Report",
                    data=json.dumps(emissions_data, indent=2),
                    file_name="hyperbuilding_carbon_emissions.json",
                    mime="application/json"
                )
        
        except json.JSONDecodeError:
            st.error("Invalid JSON file. Please check your file format.")
        except Exception as e:
            st.error(f"An unexpected error occurred: {e}")
    
    else:
        # Welcome and Instructions
        st.markdown("""
        ## Welcome to the Hyperbuilding Carbon Emissions Analyzer

        ### About
        An advanced tool for assessing the carbon footprint of complex architectural materials 
        in modern hyperbuilding designs.

        ### Key Features:
        - 🌍 Comprehensive material carbon emission calculations
        - 📊 Interactive data visualization
        - 📁 Sample data generation
        - 📈 Detailed emissions analysis

        ### JSON Input Requirements
        ```json
        [
            {
                "component": "structural_core",
                "material": "concrete",
                "material_type": "high_performance",
                "density": 2.4,
                "volume": 50
            }
        ]
        ```

        #### Getting Started
        1. Generate sample data using the sidebar
        2. Upload your custom JSON file
        3. Explore detailed carbon emissions breakdown
        """)

if __name__ == "__main__":
    main()