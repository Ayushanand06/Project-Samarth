import streamlit as st
import pandas as pd
import os

@st.cache_data(show_spinner="Loading Agriculture Production Data...")
def get_agriculture_data():
    """Loads the large crop production CSV from the local data folder."""
    file_path = os.path.join('data', 'crop_production.csv') 
    try:
        df = pd.read_csv(file_path, low_memory=False)
        df.columns = [col.strip().upper() for col in df.columns]
        
       
        # Based on your CSV snippet:
        df.rename(columns={
            'CROP': 'CROP', 
            'CROP_YEAR': 'CROP_YEAR', 
            'SEASON': 'SEASON', 
            'STATE': 'STATE_NAME', 
            'AREA': 'AREA', 
            'PRODUCTION': 'PRODUCTION'
         
        }, inplace=True)

        df['PRODUCTION'] = pd.to_numeric(df['PRODUCTION'], errors='coerce').fillna(0)
        df['CROP_YEAR'] = pd.to_numeric(df['CROP_YEAR'], errors='coerce').fillna(0).astype(int)
        df['STATE_NAME'] = df['STATE_NAME'].str.strip().str.upper()
        df['CROP'] = df['CROP'].str.strip().str.upper()
        return df
    except FileNotFoundError:
        st.error("FATAL: `crop_production.csv` not found. Please place your crop data CSV in the `data` folder.")
        return pd.DataFrame()

@st.cache_data(show_spinner="Loading Rainfall Data...")
def get_rainfall_data():
    """Loads the large rainfall CSV from the local data folder."""
    file_path = os.path.join('data', 'rainfall.csv') 
    try:
        df = pd.read_csv(file_path)
        df.columns = [col.strip().upper() for col in df.columns]
        df.rename(columns={'ANN': 'ANNUAL'}, inplace=True)
        df['SUBDIVISION'] = df['SUBDIVISION'].str.strip().str.upper()
        for col in df.columns:
            if col not in ['SUBDIVISION']:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        return df
    except FileNotFoundError:
        st.error("FATAL: `rainfall.csv` not found. Please place your rainfall data CSV in the `data` folder.")
        return pd.DataFrame()