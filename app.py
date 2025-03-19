import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
import math
from datetime import datetime
from data import load_research_data, get_complete_data
from utils import (
    calculate_statistics,
    create_summary_table,
    create_heatmap,
    create_pie_chart,
    create_time_series
)

# Define functions that were previously imported from utils.py but are now implemented here
def preprocess_data(df):
    """Placeholder for preprocessing function"""
    # In this case, we don't need to do any special preprocessing
    return df

# Set page config with theme (must be the first Streamlit command)
st.set_page_config(
    page_title="Research Data Explorer",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="📊"
)

# Define a constant for theme mode - we'll use dark mode by default since we have a dark theme in config.toml
theme_mode = "dark"

# Load the research data
df = load_research_data()
df = get_complete_data(df)  # Ensure all year/pathogen combinations exist

# Filter out all entries with "Unknown" category - keep only positive and negative data
df['Unknown'] = 0  # Set all Unknown values to 0 to remove them from calculations and visualizations

# Simplified CSS that won't break the page layout
st.markdown("""
<style>
/* Metrics styling */
.metrics-card {
  border-radius: 4px;
  padding: 0.5rem;
  margin: 0.5rem 0;
  box-shadow: 0 1px 2px rgba(0,0,0,0.05);
}

.metric-label {
  font-size: 0.7rem;
  font-weight: 500;
}

.metric-value {
  font-size: 1.1rem;
  font-weight: 600;
}

/* Chart container */
.chart-container {
  padding: 0.5rem;
  border-radius: 4px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.08);
  margin-bottom: 0.5rem;
}

/* Sidebar enhancements */
.sidebar-header {
  font-size: 1rem;
  font-weight: 600;
  margin-bottom: 0.3rem;
}

.sidebar-section {
  margin-bottom: 0.8rem;
}

/* Footer */
.app-footer {
  display: flex;
  justify-content: space-between;
  margin-top: 1rem;
  padding-top: 0.5rem;
  font-size: 0.7rem;
}
</style>
""", unsafe_allow_html=True)

# Theme selector in the corner
col1, col2 = st.columns([9, 1])
with col2:
    # We'll remove our custom theme toggle and add a note about using the built-in theme selector
    st.markdown("""
    <div style="text-align: right; font-size: 0.8rem;">
        Use ⋮ → Settings → Theme to toggle dark/light mode
    </div>
    """, unsafe_allow_html=True)
    
# The theme is now controlled by Streamlit's built-in system via .streamlit/config.toml
# No need for our JavaScript theme application

def get_theme_colors(mode):
    """Return a dictionary of colors based on the selected theme mode."""
    # Default to light theme colors (can be overridden by Streamlit's theme system)
    return {
        "background": "#FFFFFF",
        "text": "#333333",
        "secondary_text": "#666666",
        "card_bg": "#f8f9fa",
        "border": "rgba(0,0,0,0.1)",
        "highlight": "#0077FF",
        "grid": "#EEEEEE",
        "input_background": "#FFFFFF",
        "input_text": "#333333",
        "slider_color": "#333333",
        "control_label": "#333333"
    }

# Get theme colors based on current mode
theme_colors = get_theme_colors(theme_mode)  # Use a single, consistent theme

# Apply consistent styling based on theme
theme_style = f"""
<style>
    /* Apply theme to main elements */
    .stApp {{
        background-color: {theme_colors["background"]};
        color: {theme_colors["text"]};
    }}
    
    /* Sidebar styling */
    section[data-testid="stSidebar"] {{
        background-color: {theme_colors["background"]};
    }}
    
    /* Make checkbox more visible */
    [data-testid="stCheckbox"] {{
        background-color: {theme_colors["card_bg"]};
        padding: 10px !important;
        border-radius: 5px;
        border: 1px solid {theme_colors["border"]};
        margin: 10px 0 !important;
    }}
    
    /* Make multiselect more visible */
    [data-testid="stMultiSelect"] {{
        background-color: {theme_colors["card_bg"]};
        padding: 10px !important;
        border-radius: 5px;
        border: 1px solid {theme_colors["border"]};
        margin: 10px 0 !important;
    }}
    
    /* Fix selectbox display */
    [data-testid="stSelectbox"] {{
        background-color: {theme_colors["card_bg"]};
        padding: 10px !important;
        border-radius: 5px;
        border: 1px solid {theme_colors["border"]};
        margin: 10px 0 !important;
    }}
    
    /* Additional styles for select boxes */
    [data-testid="stSelectbox"] [role="combobox"] {{
        background-color: white !important;
        color: #333333 !important;
    }}
    
    /* Fix dropdown menus and multiselect inputs */
    [data-baseweb="select"] input,
    [data-baseweb="select"] [data-baseweb="input"],
    [data-baseweb="select"] [data-baseweb="tag"],
    [data-baseweb="select"] .stMultiSelect, 
    [data-baseweb="select"] div[data-testid="stMultiSelect"] {{
        background-color: white !important;
        color: #333333 !important;
    }}
    
    /* Fix arrows and icons in selects */
    [data-testid="stSelectbox"] svg,
    [data-testid="stMultiSelect"] svg {{
        fill: {theme_colors["text"]} !important;
    }}
    
    /* Fix dropdown menu appearance */
    div[data-baseweb="popover"],
    div[data-baseweb="popover"] div[role="listbox"],
    div[data-baseweb="select"] div[role="listbox"] {{
        background-color: white !important;
        border: 1px solid {theme_colors["border"]} !important;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1) !important;
        color: #333333 !important;
    }}
    
    /* Fix dropdown option colors */
    div[data-baseweb="menu"] ul li,
    div[data-baseweb="menu"] ul li button,
    div[role="listbox"] ul li,
    div[role="listbox"] div {{
        color: #333333 !important;
        background-color: white !important;
    }}
    
    div[data-baseweb="menu"] ul li:hover,
    div[role="listbox"] ul li:hover {{
        background-color: {theme_colors["highlight"]} !important;
        color: white !important;
    }}
    
    /* Warning and info boxes */
    [data-testid="stAlert"] {{
        margin: 10px 0 !important;
    }}
    
    /* Metrics styling */
    .metrics-card {{
        background-color: {theme_colors["card_bg"]};
        border-radius: 4px;
        padding: 0.5rem;
        margin: 0.5rem 0;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05);
    }}
    .metric-label {{
        font-size: 0.7rem;
        font-weight: 500;
        color: {theme_colors["secondary_text"]};
    }}
    .metric-value {{
        font-size: 1.1rem;
        font-weight: 600;
        color: {theme_colors["text"]};
    }}
    
    /* Chart container */
    .chart-container {{
        background-color: {theme_colors["background"]};
        border: 1px solid {theme_colors["border"]};
        border-radius: 4px;
        padding: 0.5rem;
        margin-bottom: 0.5rem;
    }}
    
    /* Fix various Streamlit elements */
    .sidebar-header {{
        color: {theme_colors["text"]};
    }}
    
    /* Fix labels */
    label, div[data-baseweb] {{
        color: {theme_colors["text"]} !important;
    }}
    
    /* Fix multiselect colors */
    div[data-baseweb="select"] span {{
        color: #333333 !important;
    }}
    
    /* Fix dropdown containers */
    div[data-baseweb="select"] > div,
    div[data-baseweb="select-container"] > div {{
        background-color: white !important;
    }}

    /* Fix input fields */
    input, select, textarea, .stTextInput input, .stNumberInput input {{
        color: #333333 !important;
        background-color: white !important;
    }}

    /* Fix dropdown items */
    [data-testid="stSelectbox"] div, 
    [data-testid="stSelectbox"] span, 
    [data-testid="stSelectbox"] option {{
        color: #333333 !important;
    }}
    
    /* Style select options */
    option {{
        background-color: white !important;
        color: #333333 !important;
    }}

    /* Fix all text in widgets */
    .stMarkdown, .stButton, .stSlider {{
        color: {theme_colors["text"]} !important;
    }}
    
    /* Fix all text in labels */
    p, span, label, h1, h2, h3, h4, h5, h6, div {{
        color: {theme_colors["text"]} !important;
    }}
    
    /* Make radio buttons more visible */
    [data-testid="stRadio"] > div {{
        border-radius: 5px;
        padding: 10px !important;
        background-color: {theme_colors["card_bg"]};
        border: 1px solid {theme_colors["border"]};
    }}
    
    /* Make radio buttons text more visible */
    [data-testid="stRadio"] label {{
        color: {theme_colors["text"]} !important;
        font-weight: 500;
    }}
    
    /* Fix slider values */
    [data-testid="stSlider"] [data-testid="stThumbValue"] {{
        color: {theme_colors["slider_color"]} !important;
        font-weight: bold;
    }}
    
    /* Fix slider track */
    [data-testid="stSlider"] [data-testid="stTickBar"] > div {{
        background-color: {theme_colors["secondary_text"]} !important;
    }}
    
    /* Style the selectbox dropdown */
    [data-testid="stSelectbox"] ul {{
        background-color: white !important;
        border: 1px solid {theme_colors["border"]};
    }}
    
    [data-testid="stSelectbox"] ul li {{
        color: #333333 !important;
    }}
    
    /* Style checkboxes */
    [data-testid="stCheckbox"] > label > div[role="checkbox"] {{
        border-color: {theme_colors["secondary_text"]} !important;
    }}
    
    /* Fix widget labels */
    [data-testid="stWidgetLabel"] {{
        color: {theme_colors["control_label"]} !important;
        font-weight: 600 !important;
    }}
    
    /* Additional fixes for specific elements */
    div[data-testid="stVerticalBlock"] div[data-baseweb="select"] div {{
        background-color: white !important;
    }}
    
    /* Fix multiselect container */
    div[data-baseweb="select-container"] {{
        background-color: white !important;
    }}
    
    /* Override any dark theme styling for dropdowns */
    section[data-testid="stSidebar"] [data-baseweb="select"] div:not([class]),
    section[data-testid="stSidebar"] [data-baseweb="select"] input,
    section[data-testid="stSidebar"] [data-baseweb="select"] [data-testid] {{
        background-color: white !important;
        color: #333333 !important;
    }}
    
    /* Container styling */
    div.stButton > button {{
        font-weight: 500 !important;
        border-radius: 4px !important;
    }}
    
    /* Tabs and container background fixes */
    div.row-widget.stRadio > div[role="radiogroup"] {{
        background-color: white !important;
    }}
    
    div.stTabs [data-testid="stVerticalBlock"] {{
        background-color: white !important;
    }}
    
    .stTabs [data-baseweb="tab-list"] button[data-baseweb="tab"] {{
        background-color: white !important;
    }}
    
    /* Button hover effect should not show gray */
    div.stButton > button:hover {{
        background-color: #fafafa !important;
    }}
    
    /* Make checkboxes more compact */
    div[data-testid="stCheckbox"] {{
        margin-bottom: 0.3rem !important;
        padding: 0 !important;
    }}
    
    /* Add spacing between checkbox containers in the same row */
    div.row-widget.stHorizontal > div:first-child {{
        margin-right: 4px !important;
    }}
    
    div.row-widget.stHorizontal > div:last-child {{
        margin-left: 4px !important;
    }}
</style>
"""
st.markdown(theme_style, unsafe_allow_html=True)

# Set up sidebar and UI
st.sidebar.markdown(f"""
<div style='font-size: 1.2rem; font-weight: 600; margin-bottom: 0.5rem; color: {theme_colors["text"]};'>
Data Visualization
</div>
<hr style='margin: 0.2rem 0 0.5rem 0; opacity: 0.2;'>
""", unsafe_allow_html=True)

# Initialize session state for pathogen selection if it doesn't exist
if 'show_pathogen_selector' not in st.session_state:
    st.session_state.show_pathogen_selector = False

if 'selected_pathogens' not in st.session_state:
    st.session_state.selected_pathogens = []
    
if 'select_all' not in st.session_state:
    st.session_state.select_all = False

# All pathogens for selection
all_pathogens = sorted(df["Pathogen"].unique())

# Define categories based on pathogen types
pathogen_categories = {
    "Bacteria": ["Bartonella", "Borrelia", "Brucella", "Chlamydia", "Eubacteria", "Helicobacter", 
                "Lues", "Mycobacteria", "Nocardien", "Tropheryma whipp", "Tularensis", "Yersina"],
    "Viruses": ["SARS-CoV2", "EBV", "HHV8", "HPV", "HSV1&2", "MCPyV", "MV Zytomeg", "Varizella"],
    "Fungi": ["Aspergilus", "Mucor-Mykosen", "Panfungal"],
    "Parasites": ["Echinococcus", "Leishmania"]
}

# Pathogen selection helper functions
def toggle_pathogen_selector():
    st.session_state.show_pathogen_selector = not st.session_state.show_pathogen_selector
    
def select_all_pathogens():
    # Select the first 18 pathogens (or all if less than 18)
    st.session_state.selected_pathogens = all_pathogens[:18].copy()
    
def clear_all_pathogens():
    st.session_state.selected_pathogens = []
    
def update_filter_value(value):
    st.session_state.pathogen_filter = value

# Create a button that shows the current selection count and opens the selector
selected_count = len(st.session_state.selected_pathogens)
selector_label = f"Select Pathogens ({selected_count} selected)" if selected_count > 0 else "Select Pathogens"

# Create a container for the selector button and the modal
pathogen_selector_container = st.sidebar.container()

with pathogen_selector_container:
    # When selector is closed, show a single button
    if not st.session_state.show_pathogen_selector:
        toggle_label = f"Pathogens" + (f" ({selected_count})" if selected_count > 0 else "")
        st.button(
            toggle_label,
            key="toggle_pathogen_selector",
            on_click=toggle_pathogen_selector,
            help="Expand pathogen selector",
            type="secondary",
            use_container_width=True
        )
    else:
        # When selector is open, show header row with title and close button
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"<h3 style='font-size: 1.1rem; margin-bottom: 0;'>Pathogens ({selected_count})</h3>", unsafe_allow_html=True)
        with col2:
            st.button(
                "Done", 
                on_click=toggle_pathogen_selector,
                key="done_pathogen_selection_top",
                type="secondary",
                use_container_width=True
            )
    
    # If the selector should be shown, create a tabbed interface for pathogen selection
    if st.session_state.show_pathogen_selector:
        # First apply styling for the entire selector UI
        st.markdown("""
        <style>
        /* Container styling */
        div.stButton > button {
            font-weight: 500 !important;
            border-radius: 4px !important;
        }
        
        /* Tabs and container background fixes */
        div.row-widget.stRadio > div[role="radiogroup"] {
            background-color: white !important;
        }
        
        div.stTabs [data-testid="stVerticalBlock"] {
            background-color: white !important;
        }
        
        .stTabs [data-baseweb="tab-list"] button[data-baseweb="tab"] {
            background-color: white !important;
        }
        
        /* Button hover effect should not show gray */
        div.stButton > button:hover {
            background-color: #fafafa !important;
        }
        
        /* Main selector styling */
        div.stTabs {
            background-color: white !important;
            border: 1px solid #e0e0e0 !important;
            border-radius: 5px !important;
            overflow: hidden !important;
            margin-top: 8px !important;
        }
        
        /* Tab list styling */
        div.stTabs > div:first-child {
            background-color: white !important;
            border-bottom: 1px solid #e0e0e0 !important;
        }
        
        /* Individual tab styling */
        button[role="tab"] {
            font-size: 0.8rem !important;
            font-weight: 500 !important;
            padding: 0.3rem 0.7rem !important;
            min-width: auto !important;
            background-color: white !important;
        }
        
        /* Active tab styling */
        button[role="tab"][aria-selected="true"] {
            background-color: white !important;
            border-bottom: 3px solid #4263eb !important;
            border-radius: 0 !important;
            margin-bottom: -1px !important;
        }
        
        /* Tab panel content */
        [data-baseweb="tab-panel"] {
            padding: 5px 3px 0 3px !important;
            background-color: white !important;
        }
        
        /* Checkbox styling */
        [data-testid="stCheckbox"] {
            background-color: white !important;
            border: 1px solid #e0e0e0 !important;
            border-radius: 4px !important;
            padding: 2px 8px !important;
            margin: 1px 0 !important;
            height: 28px !important;
            display: flex !important;
            align-items: center !important;
        }
        
        /* Hover effect for checkboxes */
        [data-testid="stCheckbox"]:hover {
            background-color: #f8f9fa !important;
            border-color: #bdc3c7 !important;
        }
        
        /* Checkbox selections */
        [data-testid="stCheckbox"] > label {
            display: flex !important;
            align-items: center !important;
            width: 100% !important;
        }
        
        /* Selected checkbox styling */
        [data-testid="stCheckbox"][data-baseweb="checkbox"][data-checked="true"] {
            background-color: #f0f7ff !important;
            border-color: #4285f4 !important;
        }
        
        /* Checkbox label text */
        [data-testid="stCheckbox"] > label > div:last-child {
            white-space: nowrap !important;
            overflow: hidden !important;
            text-overflow: ellipsis !important;
        }
        
        /* Filter input styling */
        [data-testid="stTextInput"] > div {
            border-radius: 4px !important;
        }
        
        /* Vertical spacing reduction in selector */
        [data-testid="stVerticalBlock"] > div {
            padding-bottom: 2px !important; 
        }
        
        /* Reduce space between columns */
        div.row-widget.stHorizontal {
            gap: 8px !important;
        }
        
        /* Tab list container */
        div[data-testid="stVerticalBlock"] div.stTabs > div:first-child {
            padding: 0 !important;
            margin: 0 !important;
        }
        
        /* Make tabs more compact */
        div[data-testid="stHorizontalBlock"] {
            gap: 0 !important;
            padding: 0 !important;
        }
        
        /* Make checkboxes more compact and add vertical spacing */
        div[data-testid="stCheckbox"] {{
            margin-bottom: 0 !important;
            padding: 1px 0 !important;
            height: auto !important;
            line-height: 1 !important;
        }}
        
        /* Target the label part of the checkbox */
        div[data-testid="stCheckbox"] label {{
            padding: 0 !important;
            font-size: 0.85rem !important;
        }}
        
        /* Ensure horizontal rows have proper margins */
        .stTabs div.row-widget.stHorizontal {{
            margin-bottom: 3px !important;
        }}
        
        /* Add spacing between checkbox columns */
        .stTabs [data-baseweb="tab-panel"] div.row-widget.stHorizontal > div {{
            padding: 0 5px !important;
        }}
        </style>
        """, unsafe_allow_html=True)
        
        # Display warning if max pathogens are selected
        if len(st.session_state.selected_pathogens) >= 18:
            st.warning("Maximum selection limit (18 pathogens) reached", icon="⚠️")
        
        # Action buttons for Select All and Clear All in a more subtle row
        col1, col2 = st.columns(2)
        with col1:
            st.button("Select All", on_click=select_all_pathogens, key="select_all_btn", use_container_width=True, type="secondary")
        with col2:
            st.button("Clear", on_click=clear_all_pathogens, key="clear_all_btn", use_container_width=True, type="secondary")
        
        # Add custom CSS for compact UI spacing
        st.markdown("""
        <style>
        /* Compact buttons and inputs */
        div[data-testid="stButton"] button {
            padding: 0.25rem 1rem !important;
            height: 2rem !important;
            margin: 0.1rem 0 !important;
        }
        
        div[data-testid="stVerticalBlock"] > div {
            padding-bottom: 0.5rem !important;
        }
        
        /* Compact tab styling */
        .stTabs [data-baseweb="tab-list"] {{
            gap: 0px !important;
        }}
        
        .stTabs [data-baseweb="tab"] {{
            padding: 5px 8px !important;
            height: auto !important;
        }}
        
        /* Reduce space between tab panels */
        .stTabs [data-baseweb="tab-panel"] {{
            padding-top: 0.5rem !important;
        }}
        
        /* Make checkboxes more compact and add vertical spacing */
        div[data-testid="stCheckbox"] {{
            margin-bottom: 0.1rem !important;
            padding: 0 !important;
            height: 1.4rem !important;
        }}
        
        /* Add small vertical gap between rows */
        div.row-widget.stHorizontal {{
            margin-bottom: 4px !important;
        }}
        
        /* Add spacing between checkbox columns */
        .stTabs [data-baseweb="tab-panel"] div.row-widget.stHorizontal > div {{
            padding: 0 8px !important;
        }}
        </style>
        """, unsafe_allow_html=True)
        
        # Create tabs for different pathogen types
        tab_bacteria, tab_viruses, tab_fungi, tab_parasites = st.tabs([
            "Bacteria", 
            "Viruses", 
            "Fungi", 
            "Parasites"
        ])
        
        # Add custom CSS for checkboxes - use minimal styling to avoid conflicts
        st.markdown("""
        <style>
        /* More compact checkboxes */
        label[data-baseweb="checkbox"] {
            margin-top: 0 !important;
            margin-bottom: 0 !important;
            padding-top: 0 !important;
            padding-bottom: 0 !important;
            line-height: 1 !important;
            min-height: 0 !important;
        }
        
        /* Target the wrapper around checkboxes to reduce vertical spacing */
        div[data-testid="element-container"] {
            margin-top: -3px !important;
            margin-bottom: -3px !important;
            padding-top: 0 !important;
            padding-bottom: 0 !important;
        }
        
        /* Make the actual checkbox smaller */
        [data-baseweb="checkbox"] [data-testid="stCheckbox"] {
            transform: scale(0.9);
        }
        
        /* Make tab buttons closer together */
        [data-baseweb="tab-list"] {
            gap: 0 !important;
        }
        
        /* Reduce padding inside tab buttons */
        [data-baseweb="tab"] {
            padding-left: 8px !important;
            padding-right: 8px !important;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Tab for Bacteria
        with tab_bacteria:
            bacteria_list = pathogen_categories["Bacteria"]
            
            if not bacteria_list:
                st.caption("No bacteria available")
            else:
                # Simple columns with no extra containers
                bacteria_columns = st.columns([1, 0.05, 1])
                
                # Calculate the midpoint
                half_point = len(bacteria_list) // 2 + len(bacteria_list) % 2
                
                # First column of bacteria
                with bacteria_columns[0]:
                    for pathogen in bacteria_list[:half_point]:
                        is_selected = pathogen in st.session_state.selected_pathogens
                        if st.checkbox(
                            pathogen, 
                            value=is_selected, 
                            key=f"bacteria_{pathogen}",
                            label_visibility="visible"
                        ):
                            if pathogen not in st.session_state.selected_pathogens:
                                if len(st.session_state.selected_pathogens) < 18:
                                    st.session_state.selected_pathogens.append(pathogen)
                        else:
                            if pathogen in st.session_state.selected_pathogens:
                                st.session_state.selected_pathogens.remove(pathogen)
                
                # Empty spacer column
                with bacteria_columns[1]:
                    st.write("")
                
                # Second column of bacteria
                with bacteria_columns[2]:
                    for pathogen in bacteria_list[half_point:]:
                        is_selected = pathogen in st.session_state.selected_pathogens
                        if st.checkbox(
                            pathogen, 
                            value=is_selected, 
                            key=f"bacteria_{pathogen}_col2",
                            label_visibility="visible"
                        ):
                            if pathogen not in st.session_state.selected_pathogens:
                                if len(st.session_state.selected_pathogens) < 18:
                                    st.session_state.selected_pathogens.append(pathogen)
                        else:
                            if pathogen in st.session_state.selected_pathogens:
                                st.session_state.selected_pathogens.remove(pathogen)
        
        # Tab for Viruses
        with tab_viruses:
            virus_list = pathogen_categories["Viruses"]
            
            if not virus_list:
                st.caption("No viruses available")
            else:
                # Simple columns with no extra containers
                virus_columns = st.columns([1, 0.05, 1])
                
                # Calculate the midpoint
                half_point = len(virus_list) // 2 + len(virus_list) % 2
                
                # First column of viruses
                with virus_columns[0]:
                    for pathogen in virus_list[:half_point]:
                        is_selected = pathogen in st.session_state.selected_pathogens
                        if st.checkbox(
                            pathogen, 
                            value=is_selected, 
                            key=f"virus_{pathogen}",
                            label_visibility="visible"
                        ):
                            if pathogen not in st.session_state.selected_pathogens:
                                if len(st.session_state.selected_pathogens) < 18:
                                    st.session_state.selected_pathogens.append(pathogen)
                        else:
                            if pathogen in st.session_state.selected_pathogens:
                                st.session_state.selected_pathogens.remove(pathogen)
                
                # Empty spacer column
                with virus_columns[1]:
                    st.write("")
                
                # Second column of viruses
                with virus_columns[2]:
                    for pathogen in virus_list[half_point:]:
                        is_selected = pathogen in st.session_state.selected_pathogens
                        if st.checkbox(
                            pathogen, 
                            value=is_selected, 
                            key=f"virus_{pathogen}_col2",
                            label_visibility="visible"
                        ):
                            if pathogen not in st.session_state.selected_pathogens:
                                if len(st.session_state.selected_pathogens) < 18:
                                    st.session_state.selected_pathogens.append(pathogen)
                        else:
                            if pathogen in st.session_state.selected_pathogens:
                                st.session_state.selected_pathogens.remove(pathogen)
        
        # Tab for Fungi
        with tab_fungi:
            fungi_list = pathogen_categories["Fungi"]
            
            if not fungi_list:
                st.caption("No fungi available")
            else:
                # Simple columns with no extra containers
                fungi_columns = st.columns([1, 0.05, 1])
                
                # Calculate the midpoint
                half_point = len(fungi_list) // 2 + len(fungi_list) % 2
                
                # First column of fungi
                with fungi_columns[0]:
                    for pathogen in fungi_list[:half_point]:
                        is_selected = pathogen in st.session_state.selected_pathogens
                        if st.checkbox(
                            pathogen, 
                            value=is_selected, 
                            key=f"fungi_{pathogen}",
                            label_visibility="visible"
                        ):
                            if pathogen not in st.session_state.selected_pathogens:
                                if len(st.session_state.selected_pathogens) < 18:
                                    st.session_state.selected_pathogens.append(pathogen)
                        else:
                            if pathogen in st.session_state.selected_pathogens:
                                st.session_state.selected_pathogens.remove(pathogen)
                
                # Empty spacer column
                with fungi_columns[1]:
                    st.write("")
                
                # Second column of fungi
                with fungi_columns[2]:
                    for pathogen in fungi_list[half_point:]:
                        is_selected = pathogen in st.session_state.selected_pathogens
                        if st.checkbox(
                            pathogen, 
                            value=is_selected, 
                            key=f"fungi_{pathogen}_col2",
                            label_visibility="visible"
                        ):
                            if pathogen not in st.session_state.selected_pathogens:
                                if len(st.session_state.selected_pathogens) < 18:
                                    st.session_state.selected_pathogens.append(pathogen)
                        else:
                            if pathogen in st.session_state.selected_pathogens:
                                st.session_state.selected_pathogens.remove(pathogen)
        
        # Tab for Parasites
        with tab_parasites:
            parasite_list = pathogen_categories["Parasites"]
            
            if not parasite_list:
                st.caption("No parasites available")
            else:
                # Simple columns with no extra containers
                parasite_columns = st.columns([1, 0.05, 1])
                
                # Calculate the midpoint
                half_point = len(parasite_list) // 2 + len(parasite_list) % 2
                
                # First column of parasites
                with parasite_columns[0]:
                    for pathogen in parasite_list[:half_point]:
                        is_selected = pathogen in st.session_state.selected_pathogens
                        if st.checkbox(
                            pathogen, 
                            value=is_selected, 
                            key=f"parasite_{pathogen}",
                            label_visibility="visible"
                        ):
                            if pathogen not in st.session_state.selected_pathogens:
                                if len(st.session_state.selected_pathogens) < 18:
                                    st.session_state.selected_pathogens.append(pathogen)
                        else:
                            if pathogen in st.session_state.selected_pathogens:
                                st.session_state.selected_pathogens.remove(pathogen)
                
                # Empty spacer column
                with parasite_columns[1]:
                    st.write("")
                
                # Second column of parasites
                with parasite_columns[2]:
                    for pathogen in parasite_list[half_point:]:
                        is_selected = pathogen in st.session_state.selected_pathogens
                        if st.checkbox(
                            pathogen, 
                            value=is_selected, 
                            key=f"parasite_{pathogen}_col2",
                            label_visibility="visible"
                        ):
                            if pathogen not in st.session_state.selected_pathogens:
                                if len(st.session_state.selected_pathogens) < 18:
                                    st.session_state.selected_pathogens.append(pathogen)
                        else:
                            if pathogen in st.session_state.selected_pathogens:
                                st.session_state.selected_pathogens.remove(pathogen)

# Store the currently selected pathogens for use in filtering
selected_pathogens = st.session_state.selected_pathogens

# If no pathogens selected, set a default one to avoid errors
if not selected_pathogens:
    selected_pathogens = [all_pathogens[0]]
    
# Initialize reordering mode in session state if it doesn't exist
if 'reordering_mode' not in st.session_state:
    st.session_state.reordering_mode = False
    
# Helper function to toggle reordering mode
def toggle_reordering_mode():
    st.session_state.reordering_mode = not st.session_state.reordering_mode
    
# Helper function to move pathogen up in the list
def move_pathogen_up(index):
    if index > 0:
        pathogens = st.session_state.selected_pathogens.copy()
        pathogens.insert(index-1, pathogens.pop(index))
        st.session_state.selected_pathogens = pathogens

# Helper function to move pathogen down in the list
def move_pathogen_down(index):
    if index < len(st.session_state.selected_pathogens) - 1:
        pathogens = st.session_state.selected_pathogens.copy()
        pathogens.insert(index+1, pathogens.pop(index))
        st.session_state.selected_pathogens = pathogens
    
# Display the currently selected pathogens as tags or reordering interface
if selected_pathogens:
    # Display header and reordering button
    col1, col2 = st.sidebar.columns([0.6, 0.4])
    with col1:
        st.markdown("### Selected Pathogens:")
    with col2:
        if st.session_state.reordering_mode:
            st.button(
                "Done",
                key="toggle_reordering_button",
                on_click=toggle_reordering_mode,
                help="Toggle reordering mode for pathogens",
                type="secondary"
            )
        else:
            st.button(
                "Reorder",
                key="toggle_reordering_button",
                on_click=toggle_reordering_mode,
                help="Toggle reordering mode for pathogens",
                type="secondary"
            )
    
    if st.session_state.reordering_mode:
        # Display the reordering interface
        st.sidebar.markdown("""
        <style>
        .reorder-item {
            background-color: #f0f0f0;
            padding: 4px 8px;
            margin-bottom: 6px;
            border-radius: 4px;
            display: flex;
            align-items: center;
        }
        .reorder-instruction {
            font-size: 0.8rem;
            color: #888;
            margin-bottom: 10px;
        }
        .pathogen-name {
            flex-grow: 1;
            padding: 6px 8px;
            background-color: white;
            border-radius: 3px;
            text-align: center;
            margin: 0 5px;
        }
        </style>
        <div class="reorder-instruction">
            Use the arrows to reorder the pathogens
        </div>
        """, unsafe_allow_html=True)
        
        # Display each pathogen with up/down buttons
        for i, pathogen in enumerate(selected_pathogens):
            cols = st.sidebar.columns([0.15, 0.7, 0.15])
            
            with cols[0]:
                # Move up button (disabled for first item)
                if i > 0:
                    st.button("↑", key=f"up_{i}", on_click=move_pathogen_up, args=(i,))
                else:
                    st.write("")  # Empty placeholder
                    
            with cols[1]:
                # Pathogen name
                st.markdown(f'<div class="pathogen-name">{pathogen}</div>', unsafe_allow_html=True)
                
            with cols[2]:
                # Move down button (disabled for last item)
                if i < len(selected_pathogens) - 1:
                    st.button("↓", key=f"down_{i}", on_click=move_pathogen_down, args=(i,))
                else:
                    st.write("")  # Empty placeholder
    else:
        # Display pathogens as tags when not in reordering mode
        # Create a container for the tags with flex layout
        st.sidebar.markdown("""
        <style>
        .tag-container {
            display: flex;
            flex-wrap: wrap;
            gap: 5px;
            margin-bottom: 15px;
        }
        .pathogen-tag {
            background-color: #e1e1e1;
            padding: 3px 8px;
            border-radius: 15px;
            font-size: 0.8rem;
            display: inline-block;
            margin-bottom: 5px;
        }
        </style>
        <div class="tag-container">
        """ + "".join([f'<div class="pathogen-tag">{p}</div>' for p in selected_pathogens]) + """
        </div>
        """, unsafe_allow_html=True)

# Chart selection
chart_type = st.sidebar.selectbox(
    "Chart Type",
    options=["3D Bars", "2D Stacked Bars", "Faceted Bar Chart", "Heatmap", "Time Series", "Pie Chart", "Summary Statistics"],
    index=0
)

# Initialize variables with defaults
bar_width = 0.8
bar_spacing = 0.2
opacity = 0.85
grid_visible = True
grid_width = 1.0
grid_density = 5
grid_color = "#CCCCCC"
show_zero_lines = True
show_axis_lines = True
axis_line_width = 2.0
show_values = False
scale_type = "Linear"
bar_mode = "group"  # Default bar mode for 2D charts
positive_color = "#00B050"
negative_color = "#FF4B4B"
unknown_color = "#FFC000"

# Visual controls for 3D charts
if chart_type == "3D Bars":
    st.sidebar.markdown(f"""
    <div style='font-size: 0.9rem; font-weight: 600; margin: 1rem 0 0.3rem 0; color: {theme_colors["text"]};'>
    Visual Controls
    </div>
    <hr style='margin: 0.2rem 0 0.5rem 0; opacity: 0.2;'>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.sidebar.columns(2)
    with col1:
        bar_width = st.slider("Bar Width", 0.1, 1.0, 0.8, 0.05)
    with col2:
        bar_spacing = st.slider("Bar Spacing", 0.0, 0.5, 0.2, 0.1)
    
    col1, col2 = st.sidebar.columns(2)
    with col1:
        opacity = st.slider("Opacity", 0.3, 1.0, 0.85, 0.05)
    with col2:
        grid_visible = st.checkbox("Show Grid", True)

    # Add grid customization options
    if grid_visible:
        st.sidebar.markdown("#### Grid Options")
        col1, col2 = st.sidebar.columns(2)
        with col1:
            grid_width = st.slider("Grid Width", 0.5, 5.0, 1.0, 0.5)
        with col2:
            grid_density = st.slider("Grid Density", 2, 10, 5, 1)
        
        grid_color = st.sidebar.color_picker("Grid Color", "#CCCCCC")
        
        col1, col2 = st.sidebar.columns(2)
        with col1:
            show_zero_lines = st.checkbox("Show Zero Lines", True)
        with col2:
            show_axis_lines = st.checkbox("Show Axis Lines", True)
        
        if show_axis_lines:
            axis_line_width = st.sidebar.slider("Axis Line Width", 1.0, 5.0, 2.0, 0.5)

elif chart_type == "2D Stacked Bars":
    # Controls for 2D bar charts
    st.sidebar.markdown(f"""
    <div style='font-size: 0.9rem; font-weight: 600; margin: 1rem 0 0.3rem 0; color: {theme_colors["text"]};'>
    Visual Controls
    </div>
    <hr style='margin: 0.2rem 0 0.5rem 0; opacity: 0.2;'>
    """, unsafe_allow_html=True)
    
    bar_mode = st.sidebar.radio("Bar Mode", ["group", "stack"], horizontal=True)
    grid_visible = st.sidebar.checkbox("Show Grid", True)

elif chart_type == "Faceted Bar Chart":
    # Controls for faceted bar charts
    st.sidebar.markdown(f"""
    <div style='font-size: 0.9rem; font-weight: 600; margin: 1rem 0 0.3rem 0; color: {theme_colors["text"]};'>
    Visual Controls
    </div>
    <hr style='margin: 0.2rem 0 0.5rem 0; opacity: 0.2;'>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.sidebar.columns(2)
    with col1:
        max_cols = st.slider("Max Columns", 1, 6, 4, 1)
    with col2:
        grid_visible = st.checkbox("Show Grid", True)
    
    # Control for chart proportions
    chart_aspect = st.sidebar.select_slider(
        "Chart Proportions",
        options=["Very Wide", "Wide", "Square", "Tall", "Very Tall"],
        value="Square"
    )
    
    # Map aspect ratio choice to subplot height
    aspect_ratio_map = {
        "Very Wide": 250,
        "Wide": 350,
        "Square": 450,
        "Tall": 550,
        "Very Tall": 650
    }
    subplot_height = aspect_ratio_map[chart_aspect]
    
    # Additional controls for appearance    
    col1, col2 = st.sidebar.columns(2)
    with col1:
        facet_bar_width = st.slider("Bar Width", 0.3, 0.9, 0.5, 0.05)
    with col2:
        show_values = st.checkbox("Show Values", False)
    
    # Always show all years and use individual y-scale
    show_all_year_labels = True
    uniform_y_scale = False
    # Fixed opacity at 100%
    opacity = 1.0

# Heatmap options (only for heatmap view)
if chart_type == "Heatmap":
    heatmap_value = st.sidebar.radio(
        "Heatmap Value",
        options=["Positive", "Negative", "Total"], # Changed 'Unknown' to 'Total'
        index=0
    )

# Data filters section
st.sidebar.markdown(f"""
<div style='font-size: 0.9rem; font-weight: 600; margin: 1rem 0 0.3rem 0; color: {theme_colors["text"]};'>
Data Filters
</div>
<hr style='margin: 0.2rem 0 0.5rem 0; opacity: 0.2;'>
""", unsafe_allow_html=True)

# Year range
year_range = st.sidebar.slider(
    "Year Range",
    min_value=int(df["Year"].min()),
    max_value=int(df["Year"].max()),
    value=(int(df["Year"].min()), int(df["Year"].max())),
    step=1
)

# Set color scheme based on theme
plot_bg_color = theme_colors["background"]
text_color = theme_colors["text"]

# Color settings (fixed at bottom)
st.sidebar.markdown(f"""
<div style='font-size: 0.9rem; font-weight: 600; margin: 1rem 0 0.3rem 0; color: {theme_colors["text"]};'>
Color Settings
</div>
<hr style='margin: 0.2rem 0 0.5rem 0; opacity: 0.2;'>
""", unsafe_allow_html=True)

col1, col2 = st.sidebar.columns(2)
with col1:
    positive_color = st.color_picker("Positive", "#00B050")
with col2:
    negative_color = st.color_picker("Negative", "#FF4B4B")

# Update colors dictionary with theme values
colors = {
    "positive": positive_color,
    "negative": negative_color,
    "background": plot_bg_color,
    "text": text_color,
    "total": "#9966CC"  # Purple for total counts
}

# Default camera values for all charts - matches the reset view
camera_x = 1.25
camera_y = 0.3
camera_z = 2.3
projection_type = "perspective"

# Create consistent camera configuration that will be used both for initial view and reset
camera_config = dict(
    eye=dict(x=camera_x, y=camera_y, z=camera_z),
    up=dict(x=0, y=1, z=0),  # Keep y-axis pointing up
    center=dict(x=0, y=0, z=0),
    projection=dict(type=projection_type)
)

# Filter data based on selections
filtered_df = df[
    (df["Year"] >= year_range[0]) & 
    (df["Year"] <= year_range[1]) & 
    (df["Pathogen"].isin(selected_pathogens))
].copy()  # Create a proper copy to avoid the SettingWithCopyWarning

# Update Total column for each filtered dataset
filtered_df.loc[:, "Total"] = filtered_df["Positive"] + filtered_df["Negative"]

# Main content
# Remove the title to make it more minimalistic

# Create 3D bar chart
def create_3d_bar_chart(df, bar_width, bar_spacing, opacity, colors, grid_visible, grid_width, grid_density, grid_color, show_zero_lines, show_axis_lines, axis_line_width, show_values, scale_type):
    fig = go.Figure()
    
    # Get unique values for x and z axes
    years = sorted(df["Year"].unique())
    
    # Get all pathogens from the dataframe
    df_pathogens = sorted(df["Pathogen"].unique())
    
    # Use the session state order for pathogens that are in the session state
    # but ensure we include all pathogens from the dataframe
    if hasattr(st, 'session_state') and 'selected_pathogens' in st.session_state:
        # Start with pathogens in the session state that are also in the dataframe
        pathogens = [p for p in st.session_state.selected_pathogens if p in df_pathogens]
        
        # Add any pathogens from the dataframe that weren't in the session state
        for p in df_pathogens:
            if p not in pathogens:
                pathogens.append(p)
    else:
        pathogens = df_pathogens
    
    # Calculate positions
    x_positions = {year: i for i, year in enumerate(years)}
    z_positions = {pathogen: i for i, pathogen in enumerate(pathogens)}
    
    # Generate a scale factor if using log scale
    if scale_type == "Log":
        scale_factor = lambda x: np.log1p(x) if x > 0 else 0
    else:
        scale_factor = lambda x: x
    
    # Calculate max height for scaling
    max_height = df[["Positive", "Negative"]].max().max()
    if max_height == 0:
        max_height = 1  # Prevent division by zero
    
    # Define edge line color (dark gray for contrast)
    edge_color = 'rgba(50, 50, 50, 0.8)'
    
    # Process each data point
    for index, row in df.iterrows():
        year_idx = x_positions[row["Year"]]
        pathogen_idx = z_positions[row["Pathogen"]]
        
        # Calculate heights
        neg_height = scale_factor(row["Negative"]) if row["Negative"] > 0 else 0
        pos_height = scale_factor(row["Positive"]) if row["Positive"] > 0 else 0
        # No need to handle unknown values since they are all 0
        
        # Create negative bar using a simpler approach
        if neg_height > 0:
            half_width = bar_width / 2
            
            # Create 6 separate meshes for each face of the cube
            # This approach reduces z-fighting and rendering artifacts
            
            # Bottom face (y=0)
            x = [year_idx - half_width, year_idx + half_width, year_idx + half_width, year_idx - half_width]
            z = [pathogen_idx - half_width, pathogen_idx - half_width, pathogen_idx + half_width, pathogen_idx + half_width]
            y = [0, 0, 0, 0]
            
            # Define face triangulation as lists - each triangle consists of 3 vertex indices
            i = [0, 0]  # First vertex indices
            j = [1, 2]  # Second vertex indices
            k = [2, 3]  # Third vertex indices
            
            fig.add_trace(go.Mesh3d(
                x=x, y=y, z=z,
                i=i, j=j, k=k,
                color=colors["negative"],
                opacity=1.0,
                flatshading=False,
                lighting=dict(
                    ambient=1.0,
                    diffuse=0,
                    specular=0,
                    roughness=0,
                    fresnel=0
                ),
                name="Negative",
                showlegend=False,
                hoverinfo="skip"
            ))
            
            # Add edge lines for the negative bar
            # Bottom square edges
            for edge_i in range(4):
                x_start = x[edge_i]
                z_start = z[edge_i]
                x_end = x[(edge_i+1)%4]
                z_end = z[(edge_i+1)%4]
                
                fig.add_trace(go.Scatter3d(
                    x=[x_start, x_end],
                    y=[0, 0],
                    z=[z_start, z_end],
                    mode='lines',
                    line=dict(color=edge_color, width=2),
                    showlegend=False,
                    hoverinfo='skip'
                ))
            
            # Top face (y=neg_height)
            y = [neg_height, neg_height, neg_height, neg_height]
            
            fig.add_trace(go.Mesh3d(
                x=x, y=y, z=z,
                i=i, j=j, k=k,
                color=colors["negative"],
                opacity=1.0,
                flatshading=False,
                lighting=dict(
                    ambient=1.0,
                    diffuse=0,
                    specular=0,
                    roughness=0,
                    fresnel=0
                ),
                showlegend=False,
                hoverinfo="skip"
            ))
            
            # Top square edges
            for edge_i in range(4):
                x_start = x[edge_i]
                z_start = z[edge_i]
                x_end = x[(edge_i+1)%4]
                z_end = z[(edge_i+1)%4]
                
                fig.add_trace(go.Scatter3d(
                    x=[x_start, x_end],
                    y=[neg_height, neg_height],
                    z=[z_start, z_end],
                    mode='lines',
                    line=dict(color=edge_color, width=2),
                    showlegend=False,
                    hoverinfo='skip'
                ))
            
            # Vertical edges connecting top and bottom
            for edge_i in range(4):
                fig.add_trace(go.Scatter3d(
                    x=[x[edge_i], x[edge_i]],
                    y=[0, neg_height],
                    z=[z[edge_i], z[edge_i]],
                    mode='lines',
                    line=dict(color=edge_color, width=2),
                    showlegend=False,
                    hoverinfo='skip'
                ))
            
            # Front face (x-z plane at min z)
            x = [year_idx - half_width, year_idx + half_width, year_idx + half_width, year_idx - half_width]
            y = [0, 0, neg_height, neg_height]
            z = [pathogen_idx - half_width, pathogen_idx - half_width, pathogen_idx - half_width, pathogen_idx - half_width]
            
            fig.add_trace(go.Mesh3d(
                x=x, y=y, z=z,
                i=i, j=j, k=k,
                color=colors["negative"],
                opacity=1.0,
                flatshading=False,
                lighting=dict(
                    ambient=1.0,
                    diffuse=0,
                    specular=0,
                    roughness=0,
                    fresnel=0
                ),
                showlegend=False,
                hoverinfo="skip"
            ))
            
            # Back face (x-z plane at max z)
            z = [pathogen_idx + half_width, pathogen_idx + half_width, pathogen_idx + half_width, pathogen_idx + half_width]
            
            fig.add_trace(go.Mesh3d(
                x=x, y=y, z=z,
                i=i, j=j, k=k,
                color=colors["negative"],
                opacity=1.0,
                flatshading=False,
                lighting=dict(
                    ambient=1.0,
                    diffuse=0,
                    specular=0,
                    roughness=0,
                    fresnel=0
                ),
                showlegend=False,
                hovertext=f"Year: {row['Year']}<br>Pathogen: {row['Pathogen']}<br>Negative: {row['Negative']}",
                hoverinfo="text"
            ))
            
            # Left face (y-z plane at min x)
            x = [year_idx - half_width, year_idx - half_width, year_idx - half_width, year_idx - half_width]
            y = [0, 0, neg_height, neg_height]
            z = [pathogen_idx - half_width, pathogen_idx + half_width, pathogen_idx + half_width, pathogen_idx - half_width]
            
            fig.add_trace(go.Mesh3d(
                x=x, y=y, z=z,
                i=i, j=j, k=k,
                color=colors["negative"],
                opacity=1.0,
                flatshading=False,
                lighting=dict(
                    ambient=1.0,
                    diffuse=0,
                    specular=0,
                    roughness=0,
                    fresnel=0
                ),
                showlegend=False,
                hoverinfo="skip"
            ))
            
            # Right face (y-z plane at max x) - with hover info
            x = [year_idx + half_width, year_idx + half_width, year_idx + half_width, year_idx + half_width]
            
            fig.add_trace(go.Mesh3d(
                x=x, y=y, z=z,
                i=i, j=j, k=k,
                color=colors["negative"],
                opacity=1.0,
                flatshading=False,
                lighting=dict(
                    ambient=1.0,
                    diffuse=0,
                    specular=0,
                    roughness=0,
                    fresnel=0
                ),
                showlegend=False,
                hovertext=f"Year: {row['Year']}<br>Pathogen: {row['Pathogen']}<br>Negative: {row['Negative']}",
                hoverinfo="text"
            ))
            
            # Add text annotation if requested
            if show_values:
                fig.add_trace(go.Scatter3d(
                    x=[year_idx],
                    y=[neg_height/2],
                    z=[pathogen_idx],
                    mode='text',
                    text=[str(row["Negative"])],
                    textposition="middle center",
                    showlegend=False
                ))
        
        # Create positive bar (stacked on top of negative)
        if pos_height > 0:
            half_width = bar_width / 2
            y_start = neg_height  # Start at the top of the negative bar
            
            # Bottom face (y=y_start)
            x = [year_idx - half_width, year_idx + half_width, year_idx + half_width, year_idx - half_width]
            z = [pathogen_idx - half_width, pathogen_idx - half_width, pathogen_idx + half_width, pathogen_idx + half_width]
            y = [y_start, y_start, y_start, y_start]
            
            i = [0, 0]
            j = [1, 2]
            k = [2, 3]
            
            fig.add_trace(go.Mesh3d(
                x=x, y=y, z=z,
                i=i, j=j, k=k,
                color=colors["positive"],
                opacity=1.0,
                flatshading=False,
                lighting=dict(
                    ambient=1.0,
                    diffuse=0,
                    specular=0,
                    roughness=0,
                    fresnel=0
                ),
                name="Positive",
                showlegend=False,
                hoverinfo="skip"
            ))
            
            # Add edge lines for the positive bar
            # Bottom square edges (transition between negative and positive)
            for edge_i in range(4):
                x_start = x[edge_i]
                z_start = z[edge_i]
                x_end = x[(edge_i+1)%4]
                z_end = z[(edge_i+1)%4]
                
                fig.add_trace(go.Scatter3d(
                    x=[x_start, x_end],
                    y=[y_start, y_start],
                    z=[z_start, z_end],
                    mode='lines',
                    line=dict(color=edge_color, width=2),
                    showlegend=False,
                    hoverinfo='skip'
                ))
            
            # Top face (y=y_start+pos_height)
            y = [y_start + pos_height, y_start + pos_height, y_start + pos_height, y_start + pos_height]
            
            fig.add_trace(go.Mesh3d(
                x=x, y=y, z=z,
                i=i, j=j, k=k,
                color=colors["positive"],
                opacity=1.0,
                flatshading=False,
                lighting=dict(
                    ambient=1.0,
                    diffuse=0,
                    specular=0,
                    roughness=0,
                    fresnel=0
                ),
                showlegend=False,
                hoverinfo="skip"
            ))
            
            # Top square edges
            for edge_i in range(4):
                x_start = x[edge_i]
                z_start = z[edge_i]
                x_end = x[(edge_i+1)%4]
                z_end = z[(edge_i+1)%4]
                
                fig.add_trace(go.Scatter3d(
                    x=[x_start, x_end],
                    y=[y_start + pos_height, y_start + pos_height],
                    z=[z_start, z_end],
                    mode='lines',
                    line=dict(color=edge_color, width=2),
                    showlegend=False,
                    hoverinfo='skip'
                ))
            
            # Vertical edges connecting top and bottom
            for edge_i in range(4):
                fig.add_trace(go.Scatter3d(
                    x=[x[edge_i], x[edge_i]],
                    y=[y_start, y_start + pos_height],
                    z=[z[edge_i], z[edge_i]],
                    mode='lines',
                    line=dict(color=edge_color, width=2),
                    showlegend=False,
                    hoverinfo='skip'
                ))
            
            # Front face (x-z plane at min z)
            x = [year_idx - half_width, year_idx + half_width, year_idx + half_width, year_idx - half_width]
            y = [y_start, y_start, y_start + pos_height, y_start + pos_height]
            z = [pathogen_idx - half_width, pathogen_idx - half_width, pathogen_idx - half_width, pathogen_idx - half_width]
            
            fig.add_trace(go.Mesh3d(
                x=x, y=y, z=z,
                i=i, j=j, k=k,
                color=colors["positive"],
                opacity=1.0,
                flatshading=False,
                lighting=dict(
                    ambient=1.0,
                    diffuse=0,
                    specular=0,
                    roughness=0,
                    fresnel=0
                ),
                showlegend=False,
                hoverinfo="skip"
            ))
            
            # Back face (x-z plane at max z)
            z = [pathogen_idx + half_width, pathogen_idx + half_width, pathogen_idx + half_width, pathogen_idx + half_width]
            
            fig.add_trace(go.Mesh3d(
                x=x, y=y, z=z,
                i=i, j=j, k=k,
                color=colors["positive"],
                opacity=1.0,
                flatshading=False,
                lighting=dict(
                    ambient=1.0,
                    diffuse=0,
                    specular=0,
                    roughness=0,
                    fresnel=0
                ),
                showlegend=False,
                hovertext=f"Year: {row['Year']}<br>Pathogen: {row['Pathogen']}<br>Positive: {row['Positive']}",
                hoverinfo="text"
            ))
            
            # Left face (y-z plane at min x)
            x = [year_idx - half_width, year_idx - half_width, year_idx - half_width, year_idx - half_width]
            y = [y_start, y_start, y_start + pos_height, y_start + pos_height]
            z = [pathogen_idx - half_width, pathogen_idx + half_width, pathogen_idx + half_width, pathogen_idx - half_width]
            
            fig.add_trace(go.Mesh3d(
                x=x, y=y, z=z,
                i=i, j=j, k=k,
                color=colors["positive"],
                opacity=1.0,
                flatshading=False,
                lighting=dict(
                    ambient=1.0,
                    diffuse=0,
                    specular=0,
                    roughness=0,
                    fresnel=0
                ),
                showlegend=False,
                hoverinfo="skip"
            ))
            
            # Right face (y-z plane at max x) - with hover info
            x = [year_idx + half_width, year_idx + half_width, year_idx + half_width, year_idx + half_width]
            
            fig.add_trace(go.Mesh3d(
                x=x, y=y, z=z,
                i=i, j=j, k=k,
                color=colors["positive"],
                opacity=1.0,
                flatshading=False,
                lighting=dict(
                    ambient=1.0,
                    diffuse=0,
                    specular=0,
                    roughness=0,
                    fresnel=0
                ),
                showlegend=False,
                hovertext=f"Year: {row['Year']}<br>Pathogen: {row['Pathogen']}<br>Positive: {row['Positive']}",
                hoverinfo="text"
            ))
            
            # Add text annotation if requested
            if show_values:
                fig.add_trace(go.Scatter3d(
                    x=[year_idx],
                    y=[y_start + pos_height/2],
                    z=[pathogen_idx],
                    mode='text',
                    text=[str(row["Positive"])],
                    textposition="middle center",
                    showlegend=False
                ))
    
    # Fix for pandas SettingWithCopyWarning
    filtered_df.loc[:, "Total"] = filtered_df["Positive"] + filtered_df["Negative"]
    
    # Calculate layout ranges
    x_range = [-0.5, len(years) - 0.5]  # Allow some space on both sides
    total_max_height = max(scale_factor(max_height), 1)  # Ensure at least 1 for visibility
    
    if scale_type == "Log":
        total_max_height = scale_factor(total_max_height)
    y_range = [0, total_max_height * 1.1]  # Add 10% margin at the top
    z_range = [-0.5, len(pathogens) - 0.5]  # No extra space needed with stacked bars
    
    # Set up grid color based on visibility
    grid_colors = grid_color if grid_visible else colors["background"]
    
    # Make sure camera view is properly initialized
    fig.layout.scene.camera = camera_config
    
    # Set up axis configuration to maintain correct orientation
    fig.update_layout(
        scene=dict(
            xaxis=dict(
                title="Year",
                tickvals=list(x_positions.values()),
                ticktext=list(x_positions.keys()),
                nticks=grid_density,
                gridcolor=grid_colors,
                gridwidth=grid_width,
                color=colors["text"],
                range=x_range,
                autorange=False,
                showline=show_axis_lines,
                linecolor=grid_color,
                linewidth=axis_line_width,
                showgrid=grid_visible,
                zeroline=show_zero_lines,
                zerolinecolor=grid_color,
                zerolinewidth=grid_width * 1.5
            ),
            yaxis=dict(
                title="Count" if scale_type == "Linear" else "Log Count",
                gridcolor=grid_colors,
                gridwidth=grid_width,
                nticks=grid_density,
                color=colors["text"],
                type="linear" if scale_type == "Linear" else "log",
                range=y_range,
                autorange=False,
                showline=show_axis_lines,
                linecolor=grid_color,
                linewidth=axis_line_width,
                showgrid=grid_visible,
                zeroline=show_zero_lines,
                zerolinecolor=grid_color,
                zerolinewidth=grid_width * 1.5
            ),
            zaxis=dict(
                title="Pathogen",
                tickvals=list(z_positions.values()),
                ticktext=list(z_positions.keys()),
                nticks=grid_density,
                gridcolor=grid_colors,
                gridwidth=grid_width,
                color=colors["text"],
                range=z_range,
                autorange=False,
                showline=show_axis_lines,
                linecolor=grid_color,
                linewidth=axis_line_width,
                showgrid=grid_visible,
                zeroline=show_zero_lines,
                zerolinecolor=grid_color,
                zerolinewidth=grid_width * 1.5
            ),
            camera=camera_config,  # Apply camera configuration directly
            aspectmode="manual",
            aspectratio=dict(x=1.5, y=1, z=1.2),
            dragmode="orbit",  # Change to orbit for better control of the camera
            bgcolor=colors["background"],
        ),
        scene_camera=camera_config,  # Apply camera directly to scene_camera
        width=1000,
        height=700,
        margin=dict(l=0, r=0, b=0, t=0),  # Remove top margin by setting t to 0
        showlegend=False,
        uirevision="constant",  # Keep this constant to persist camera state between updates
        modebar=dict(
            orientation="v",
            bgcolor="rgba(50, 50, 50, 0.7)" if theme_mode == "Dark" else "rgba(255, 255, 255, 0.7)",
            color=colors["text"]
        ),
        updatemenus=[
            dict(
                type="buttons",
                showactive=False,
                buttons=[
                    dict(
                        label="Reset View",
                        method="relayout",
                        args=[{
                            "scene.camera": camera_config,
                            "scene.dragmode": "orbit"
                        }]
                    )
                ],
                direction="down",
                pad={"r": 10, "t": 10},
                x=0.05,
                y=0.05,
                bgcolor="rgba(50, 50, 50, 0.7)" if theme_mode == "Dark" else "rgba(255, 255, 255, 0.7)",
                font=dict(color=colors["text"])
            )
        ],
        paper_bgcolor=colors["background"],
        plot_bgcolor=colors["background"],
        font=dict(color=colors["text"])
    )

    return fig

# Create 2D stacked bar chart
def create_2d_bar_chart(df, opacity, colors, grid_visible, show_values, bar_mode):
    # List of unique years and pathogens
    years = sorted(df["Year"].unique())
    
    # Get all pathogens from the dataframe
    df_pathogens = sorted(df["Pathogen"].unique())
    
    # Use the session state order for pathogens that are in the session state
    # but ensure we include all pathogens from the dataframe
    if hasattr(st, 'session_state') and 'selected_pathogens' in st.session_state:
        # Start with pathogens in the session state that are also in the dataframe
        pathogens = [p for p in st.session_state.selected_pathogens if p in df_pathogens]
        
        # Add any pathogens from the dataframe that weren't in the session state
        for p in df_pathogens:
            if p not in pathogens:
                pathogens.append(p)
    else:
        pathogens = df_pathogens
    
    # Initialize figure
    fig = go.Figure()
    
    # Create color sequences
    if bar_mode == "group":
        # Group mode (pathogens side by side)
        x_positions = []
        for year in years:
            for pathogen in pathogens:
                x_positions.append(f"{year} - {pathogen}")
        
        # Add traces for each data type
        for data_type, color_key in [("Positive", "positive"), ("Negative", "negative")]:
            y_values = []
            hover_texts = []
            
            for year in years:
                for pathogen in pathogens:
                    matching_rows = df[(df["Year"] == year) & (df["Pathogen"] == pathogen)]
                    if not matching_rows.empty:
                        value = matching_rows[data_type].iloc[0]
                        y_values.append(value)
                        hover_texts.append(f"{pathogen} ({year})<br>{data_type}: {value}")
                    else:
                        y_values.append(0)
                        hover_texts.append(f"{pathogen} ({year})<br>{data_type}: 0")
            
            fig.add_trace(go.Bar(
                x=x_positions,
                y=y_values,
                name=data_type,
                marker_color=colors[color_key.lower()],
                opacity=opacity,
                text=y_values if show_values else None,
                textposition="auto",
                hoverinfo="text",
                hovertext=hover_texts
            ))
    else:
        # Stack mode (by pathogen and year)
        # First, create a pivot table for better visualization
        for pathogen in pathogens:
            pathogen_data = df[df["Pathogen"] == pathogen]
            
            for data_type, color_key in [("Positive", "positive"), ("Negative", "negative")]:
                fig.add_trace(go.Bar(
                    x=pathogen_data["Year"],
                    y=pathogen_data[data_type],
                    name=f"{pathogen} - {data_type}",
                    marker_color=colors[color_key.lower()],
                    opacity=opacity,
                    text=pathogen_data[data_type] if show_values else None,
                    textposition="auto"
                ))
    
    # Update layout
    fig.update_layout(
        barmode=bar_mode,
        xaxis=dict(
            title="Year - Pathogen" if bar_mode == "group" else "Year",
            gridcolor=grid_color if grid_visible else "white"
        ),
        yaxis=dict(
            title="Count",
            gridcolor=grid_color if grid_visible else "white"
        ),
        legend=dict(
            title="Data Type" if bar_mode == "group" else "Pathogen - Data Type"
        ),
        width=1000,
        height=700,
        title="2D Bar Chart of Research Data"
    )
    
    return fig

# Create a faceted bar chart with properly handled titles
def create_faceted_bar_chart(df, opacity, colors, grid_visible, show_values, max_cols=4, uniform_y_scale=False, show_all_year_labels=True, bar_width=0.5, subplot_height=400):
    # Default grid color for both light and dark themes
    grid_color = 'rgba(211, 211, 211, 0.5)'
    
    # Get all pathogens from the dataframe
    pathogens = sorted(df["Pathogen"].unique())
    
    num_pathogens = len(pathogens)
    
    # Handle the case with no pathogens
    if num_pathogens == 0:
        # Create a simple figure with a message
        fig = go.Figure()
        fig.add_annotation(
            text="No data to display",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=20)
        )
        return fig, 300, 800
    
    # Calculate grid dimensions based on number of pathogens
    # Use max_cols to limit the number of columns
    n_cols = min(max_cols, max(1, num_pathogens))  # Ensure at least 1 column
    n_rows = max(1, math.ceil(num_pathogens / n_cols))

    # Simplified spacing constants
    v_spacing = 0.2
    h_spacing = 0.1

    # Fixed dimensions
    subplot_height = 300
    subplot_width = 300
    
    # Calculate total figure dimensions
    total_height = subplot_height * n_rows + 100  # Add space for margins
    total_width = subplot_width * n_cols + 100    # Add space for margins
    
    # Create subplot grid with titles 
    fig = make_subplots(
        rows=n_rows, 
        cols=n_cols,
        subplot_titles=pathogens,
        vertical_spacing=v_spacing,
        horizontal_spacing=h_spacing
    )
    
    # Find global y-max for consistent scaling (if uniform_y_scale is True)
    y_max = None
    if uniform_y_scale:
        # For stacked bars, we need the sum of positive and negative
        y_max = df.groupby('Pathogen')[['Positive', 'Negative']].sum().sum(axis=1).max() * 1.15
        # Set minimum value to ensure proper display even with small numbers
        y_max = max(10, y_max if y_max is not None else 10)
    
    # Add a trace for each pathogen
    for i, pathogen in enumerate(pathogens):
        # Calculate row and column position
        row = i // n_cols + 1
        col = i % n_cols + 1
        
        # Filter data for this pathogen
        pathogen_data = df[df["Pathogen"] == pathogen]
        
        # Sort by year to ensure chronological order
        pathogen_data = pathogen_data.sort_values("Year")
        
        # Only proceed if we have data
        if not pathogen_data.empty:
            # Add negative bars (bottom layer)
            fig.add_trace(
                go.Bar(
                    x=pathogen_data["Year"].astype(str),  # Convert to string to avoid dtick issues
                    y=pathogen_data["Negative"],
                    name="Negative",
                    marker_color=colors["negative"],
                    opacity=opacity,
                    showlegend=i==0,  # Only show legend for first pathogen
                    text=pathogen_data["Negative"] if show_values else None,
                    textposition="inside",
                    width=bar_width,
                    hovertemplate="Year: %{x}<br>Negative: %{y}<extra></extra>"
                ),
                row=row, col=col
            )
            
            # Add positive bars (stacked on top)
            fig.add_trace(
                go.Bar(
                    x=pathogen_data["Year"].astype(str),  # Convert to string to avoid dtick issues
                    y=pathogen_data["Positive"],
                    name="Positive",
                    marker_color=colors["positive"],
                    opacity=opacity,
                    showlegend=i==0,  # Only show legend for first pathogen
                    text=pathogen_data["Positive"] if show_values else None,
                    textposition="inside",
                    width=bar_width,
                    hovertemplate="Year: %{x}<br>Positive: %{y}<extra></extra>"
                ),
                row=row, col=col
            )
            
            # Calculate individual y-max for this pathogen
            individual_y_max = pathogen_data[['Positive', 'Negative']].sum(axis=1).max() * 1.15
            individual_y_max = max(10, individual_y_max)  # Default min value if data is small
            
            # Use global y_max if uniform scaling is requested
            max_value = y_max if uniform_y_scale and y_max is not None else individual_y_max
            
            # Update axes for this subplot
            fig.update_xaxes(
                title_text=None,
                showgrid=grid_visible,
                gridcolor=grid_color if grid_visible else "white",
                tickangle=90,  # Use vertical tick labels for years to save space
                tickfont=dict(size=10),
                row=row, col=col
            )
            
            fig.update_yaxes(
                title_text=None,
                showgrid=grid_visible,
                gridcolor=grid_color if grid_visible else "white",
                range=[0, max_value],
                tickfont=dict(size=10),
                row=row, col=col,
                tickformat=",d"  # Format ticks as integers with commas for thousands
            )
        else:
            # Add an empty trace if no data is available for this pathogen
            fig.add_trace(
                go.Bar(
                    x=[],
                    y=[],
                    name="No Data",
                    showlegend=False
                ),
                row=row, col=col
            )
            
            # Add annotation for empty subplot
            fig.add_annotation(
                text="No data available",
                xref=f"x{i+1}", yref=f"y{i+1}",
                x=0.5, y=0.5,
                showarrow=False,
                font=dict(size=12, color="gray"),
                row=row, col=col
            )
    
    # Update layout with fixed dimensions
    fig.update_layout(
        barmode='stack',
        height=total_height,
        width=total_width,
        bargap=0.15,
        bargroupgap=0.05,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5
        ),
        title=None
    )
    
    # Update subplot titles
    fig.update_annotations(
        font=dict(
            size=12,
            color="#333333"
        )
    )
    
    return fig, total_height, total_width

# Display chart with metrics
if not filtered_df.empty:
    with st.spinner("Loading..."):
        # Chart container
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        
        if chart_type == "3D Bars":
            # Create and display chart
            fig = create_3d_bar_chart(filtered_df, bar_width, bar_spacing, opacity, colors, grid_visible, grid_width, grid_density, grid_color, show_zero_lines, show_axis_lines, axis_line_width, show_values, scale_type)
            
            # Make sure colors match the theme
            fig.update_layout(
                font=dict(color=text_color),
                scene=dict(
                    xaxis=dict(color=text_color, gridcolor=grid_color if grid_visible else plot_bg_color, gridwidth=grid_width),
                    yaxis=dict(color=text_color, gridcolor=grid_color if grid_visible else plot_bg_color, gridwidth=grid_width),
                    zaxis=dict(color=text_color, gridcolor=grid_color if grid_visible else plot_bg_color, gridwidth=grid_width),
                    bgcolor=plot_bg_color
                ),
                paper_bgcolor=plot_bg_color
            )
            
            # Apply camera settings
            fig.layout.scene.camera = camera_config
            fig.update_layout(
                scene_camera=camera_config,
                scene=dict(
                    camera=camera_config,
                    dragmode="orbit"
                )
            )
            
            # Add JavaScript to ensure camera is set correctly on load
            camera_js = f"""
            <script>
                function setInitialCameraView() {{
                    // Try to find the scene div
                    let sceneDiv = document.querySelector('.plot-container .js-plotly-plot .scene');
                    if (sceneDiv) {{
                        // Access the Plotly scene camera
                        let gd = document.querySelector('.js-plotly-plot');
                        if (gd && gd._fullLayout && gd._fullLayout.scene) {{
                            // Set camera to initial position
                            Plotly.relayout(gd, {{
                                "scene.camera": {{
                                    eye: {{x: {camera_x}, y: {camera_y}, z: {camera_z}}},
                                    center: {{x: 0, y: 0, z: 0}},
                                    up: {{x: 0, y: 1, z: 0}}
                                }}
                            }});
                            console.log("Camera position set");
                            return true;
                        }}
                    }}
                    return false;
                }}
                
                // Try to set camera view with retries
                function trySetCamera(retries, delay) {{
                    if (retries <= 0) return;
                    
                    setTimeout(function() {{
                        let success = setInitialCameraView();
                        if (!success) {{
                            console.log("Retrying camera setup, attempts left: " + (retries-1));
                            trySetCamera(retries-1, delay * 1.5);
                        }}
                    }}, delay);
                }}
                
                // Wait for the DOM to be fully loaded
                document.addEventListener('DOMContentLoaded', function() {{
                    // Initial attempt
                    if (!setInitialCameraView()) {{
                        // If failed, retry with increasing delays
                        trySetCamera(5, 300);
                    }}
                }});
                
                // Also try once the page has completely loaded
                window.addEventListener('load', function() {{
                    if (!setInitialCameraView()) {{
                        trySetCamera(3, 500);
                    }}
                }});
            </script>
            """
            st.components.v1.html(camera_js, height=0)
            
            # IMPORTANT: Do not change the rendering method below. The current configuration provides optimal performance and compatibility.
            # Display the chart with proper config
            st.plotly_chart(fig, use_container_width=True, config={
                'displayModeBar': True,
                'displaylogo': False,
                'modeBarButtonsToRemove': ['resetCameraLastSave3d'],
                'scrollZoom': True,
                'toImageButtonOptions': {
                    'format': 'png',
                    'filename': f'3d_bar_chart_{datetime.now().strftime("%Y%m%d_%H%M%S")}',
                    'height': 800,
                    'width': 1200,
                    'scale': 2
                }
            })
            
        elif chart_type == "2D Stacked Bars":
            fig = create_2d_bar_chart(filtered_df, opacity, colors, grid_visible, show_values, bar_mode)
            # Apply theme colors
            fig.update_layout(
                font=dict(color=text_color),
                paper_bgcolor=plot_bg_color,
                plot_bgcolor=plot_bg_color
            )
            
            # Display the chart with download option in the modebar
            st.plotly_chart(fig, use_container_width=True, config={
                'displayModeBar': True,
                'displaylogo': False,
                'toImageButtonOptions': {
                    'format': 'png',
                    'filename': f'stacked_bar_chart_{datetime.now().strftime("%Y%m%d_%H%M%S")}',
                    'height': 800,
                    'width': 1200,
                    'scale': 2
                }
            })
            
        elif chart_type == "Heatmap":
            if heatmap_value == "Total":
                # Create a temporary dataframe with a Total column
                heatmap_df = filtered_df.copy()
                heatmap_df["Total"] = heatmap_df["Positive"] + heatmap_df["Negative"]
            else:
                heatmap_df = filtered_df
                
            fig = create_heatmap(heatmap_df, heatmap_value, colors)
            # Apply theme colors
            fig.update_layout(
                font=dict(color=text_color),
                paper_bgcolor=plot_bg_color,
                plot_bgcolor=plot_bg_color
            )
            
            # Display the chart with download option in the modebar
            st.plotly_chart(fig, use_container_width=True, config={
                'displayModeBar': True,
                'displaylogo': False,
                'toImageButtonOptions': {
                    'format': 'png',
                    'filename': f'heatmap_{datetime.now().strftime("%Y%m%d_%H%M%S")}',
                    'height': 800,
                    'width': 1200,
                    'scale': 2
                }
            })
            
        elif chart_type == "Time Series":
            fig = create_time_series(filtered_df, colors)
            # Apply theme colors
            fig.update_layout(
                font=dict(color=text_color),
                paper_bgcolor=plot_bg_color,
                plot_bgcolor=plot_bg_color
            )
            
            # Display the chart with download option in the modebar
            st.plotly_chart(fig, use_container_width=True, config={
                'displayModeBar': True,
                'displaylogo': False,
                'toImageButtonOptions': {
                    'format': 'png',
                    'filename': f'time_series_{datetime.now().strftime("%Y%m%d_%H%M%S")}',
                    'height': 800,
                    'width': 1200,
                    'scale': 2
                }
            })
            
        elif chart_type == "Pie Chart":
            fig = create_pie_chart(filtered_df, colors)
            # Apply theme colors
            fig.update_layout(
                font=dict(color=text_color),
                paper_bgcolor=plot_bg_color
            )
            
            # Display the chart with download option in the modebar
            st.plotly_chart(fig, use_container_width=True, config={
                'displayModeBar': True,
                'displaylogo': False,
                'toImageButtonOptions': {
                    'format': 'png',
                    'filename': f'pie_chart_{datetime.now().strftime("%Y%m%d_%H%M%S")}',
                    'height': 800,
                    'width': 1200,
                    'scale': 2
                }
            })
        
        elif chart_type == "Summary Statistics":
            # Calculate statistics
            stats = calculate_statistics(filtered_df)
            summary_table = create_summary_table(filtered_df)
            
            # Display statistics in cleaner columns
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total Samples", f"{stats['total_samples']:,}")
                st.metric("Positive Samples", f"{stats['total_positive']:,}")
                st.metric("Negative Samples", f"{stats['total_negative']:,}")
            
            with col2:
                st.metric("Positive Ratio", f"{stats['positive_ratio']:.2%}")
                st.metric("Negative Ratio", f"{stats['negative_ratio']:.2%}")
            
            with col3:
                st.metric("Pathogen Count", stats['pathogen_count'])
                st.metric("Year Range", f"{stats['year_range'][0]}-{stats['year_range'][1]}")
                st.metric("Number of Years", stats['years_count'])
            
            # Display summary table
            st.dataframe(summary_table, use_container_width=True)
            
        elif chart_type == "Faceted Bar Chart":
            # Create the faceted bar chart with correct sizing
            try:
                # Make sure year is integer type before creating chart
                filtered_df["Year"] = filtered_df["Year"].astype(int)
                
                fig, total_height, total_width = create_faceted_bar_chart(filtered_df, opacity, colors, grid_visible, show_values, max_cols, uniform_y_scale, show_all_year_labels, facet_bar_width, subplot_height)
                
                # Apply theme colors
                fig.update_layout(
                    font=dict(color=text_color),
                    paper_bgcolor=plot_bg_color,
                    plot_bgcolor=plot_bg_color
                )
                
                # Add a title as Streamlit markdown above the chart instead of in the Plotly figure
                st.markdown(f"""
                <h3 style='text-align: center; margin-bottom: 5px; color: {text_color};'>
                    Faceted Bar Chart
                </h3>
                <div style='text-align: center; margin-bottom: 15px; font-size: 0.9rem;'>
                    <span style='display: inline-block; width: 12px; height: 12px; background-color: {colors["positive"]}; margin-right: 5px;'></span>
                    <span style='margin-right: 15px;'>Positive</span>
                    <span style='display: inline-block; width: 12px; height: 12px; background-color: {colors["negative"]}; margin-right: 5px;'></span>
                    <span>Negative</span>
                </div>
                """, unsafe_allow_html=True)
                
                # Use direct HTML rendering for precise control over dimensions
                config = {
                    'displayModeBar': True,  # Show the mode bar to allow downloading
                    'displaylogo': False,
                    'scrollZoom': False,
                    'toImageButtonOptions': {
                        'format': 'png',
                        'filename': f'faceted_bar_chart_{datetime.now().strftime("%Y%m%d_%H%M%S")}',
                        'height': total_height+100,
                        'width': total_width+100,
                        'scale': 2
                    }
                }
                
                st.plotly_chart(fig, use_container_width=False, config=config)
            except Exception as e:
                st.error(f"Error creating faceted bar chart: {str(e)}")
                st.info("Try using fewer pathogens or different filter options.")
        
        # Close chart container
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Display metrics below chart
        if chart_type not in ["Summary Statistics"]:
            st.markdown('<div class="metrics-card">', unsafe_allow_html=True)
            metrics_cols = st.columns(5)
            
            with metrics_cols[0]:
                st.markdown(f"""
                <div class="metric-label">Years</div>
                <div class="metric-value">{year_range[1] - year_range[0] + 1}</div>
                """, unsafe_allow_html=True)
                
            with metrics_cols[1]:
                st.markdown(f"""
                <div class="metric-label">Pathogens</div>
                <div class="metric-value">{len(selected_pathogens)}</div>
                """, unsafe_allow_html=True)
                
            with metrics_cols[2]:
                total_positive = filtered_df["Positive"].sum()
                st.markdown(f"""
                <div class="metric-label">Positive</div>
                <div class="metric-value">{total_positive:,}</div>
                """, unsafe_allow_html=True)
                
            with metrics_cols[3]:
                total_negative = filtered_df["Negative"].sum()
                st.markdown(f"""
                <div class="metric-label">Negative</div>
                <div class="metric-value">{total_negative:,}</div>
                """, unsafe_allow_html=True)
                
            st.markdown('</div>', unsafe_allow_html=True)
else:
    st.warning("No data available with the current filter settings. Please adjust your filters.")

# Footer
st.markdown(f"""
<div style="display: flex; 
            justify-content: space-between; 
            margin-top: 1rem; 
            padding-top: 0.5rem; 
            border-top: 1px solid {theme_colors["border"]};
            color: {theme_colors["secondary_text"]};
            font-size: 0.7rem;">
    <span>Research Data Explorer v1.0</span>
    <span>Streamlit + Plotly</span>
</div>
""", unsafe_allow_html=True)

# End of file

