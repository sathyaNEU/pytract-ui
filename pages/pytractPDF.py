import streamlit as st
import requests
import pandas as pd
from utils.helper import *

st.title('Pytract-PDF Core')
st.markdown('---')
st.subheader("Existing PDFs")

# API Endpoints

if 'pdf_data' not in st.session_state:
    load_pdfs()

df = st.session_state.get('pdf_data').copy()
if df.empty:
    st.warning('No PDF files available to display. Please upload a file or check back later.')
else:
    
    df.insert(0, "Select", False)

    edited_df = st.data_editor(df, num_rows="dynamic", key="Public Endpoint", hide_index=True)

    selected_rows = edited_df[edited_df["Select"] == True]
    columns_to_display = [col for col in selected_rows.columns if col != 'Select']

    st.write("### Selected Files:")
    st.dataframe(selected_rows[columns_to_display], use_container_width=True, hide_index=True)

    tool_option = st.radio("Choose an option", ["Open Source (PyPDF, pdfplumber)", "Enterprise (Document Intelligence)"])

    if st.button('**Extract**'):
        if selected_rows.shape[0] == 1:
            url = selected_rows.iloc[0]["Public Endpoint"]
            body = {"url": url}
            endpoint = extract_oss_endpoint if tool_option == "Open Source (PyPDF, pdfplumber)" else extract_docint_endpoint
            
            response = requests.post(base_url + endpoint, json=body)
            if response.status_code == 200:
                st.success(f"Images and Tables Extracted Successfully, visit http://{get_local_ip()}:8501/pdf-extract-results for extraction results")
            else:
                st.error("Processing Failed")

            md_response = requests.post(base_url + extract_docling_endpoint, json=body)
            if md_response.status_code == 200:
                st.success(f"Standardized Markdown live @ {md_response.json()['url']}")
            else:
                st.error("Processing Failed")
        elif selected_rows.shape[0] == 0:
            st.warning("Select a PDF Record to start the extraction")
        else:
            st.warning("Currently our system is synchronous!\nKindly queue one process at a time!")
