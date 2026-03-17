import streamlit as st
import tempfile
import os
from processor import VideoProcessor

# Page Config
st.set_page_config(
    page_title="Cricket Analysis Tool", 
    page_icon="🏏", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Dark Theme and Aesthetics
st.markdown("""
<style>
    .stApp {
        background-color: #0e1117;
        color: #FAFAFA;
    }
    .stButton>button {
        background-color: #262730;
        color: white;
        border-radius: 8px;
        border: 1px solid #4B4B4B;
    }
    .stButton>button:hover {
        background-color: #3E3F4B;
        border-color: #FAFAFA;
    }
    h1 {
        color: #00ADB5;
    }
</style>
""", unsafe_allow_html=True)

# Application Header
st.title("🏏 Pro Cricket Analysis")
st.markdown("### AI-Powered Stance & Weight Transfer Analysis")

st.sidebar.header("Configuration")
player_name = st.sidebar.text_input("Player Name", "Virat")

# File Uploader
uploaded_file = st.file_uploader("Upload Batting Video (MP4)", type=["mp4"])

if uploaded_file is not None:
    # Save uploaded file to a temporary file
    tfile = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") 
    tfile.write(uploaded_file.read())
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Original Video")
        st.video(tfile.name)
        
    process_btn = st.button("Analyze Stance")
    
    if process_btn:
        with st.spinner('Processing video... This may take a moment.'):
            # Setup output path
            output_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
            output_path = output_file.name
            output_file.close() # Close so opencv can write to it
            
            # Process
            processor = VideoProcessor()
            processor.process_video(tfile.name, output_path, player_name=player_name)
            
            # Display Result
            with col2:
                st.subheader("Analyzed Video")
                st.video(output_path)
                
            st.success("Analysis Complete!")
            
            # Option to download
            with open(output_path, 'rb') as f:
                st.download_button('Download Analyzed Video', f, file_name='analyzed_batting.mp4')
                
            # Cleanup output (optional / automatic by OS eventually)
            
    # Cleanup input
    # os.unlink(tfile.name) 
    # Don't delete immediately so user can replay original if they want
