# mainapp.py
import streamlit as st
import os
import sys

# Projenin kök dizinini Python'un arama yoluna ekle
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from modules.image_analysis import main_page

if __name__ == "__main__":
    st.set_page_config(page_title="BronkoVision", layout="wide")
    main_page()