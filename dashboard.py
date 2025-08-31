import streamlit as st
import pandas as pd
import plotly.express as px

# Title and description
st.set_page_config(page_title="District Competitiveness Dashboard - Dairy Sector", layout="wide")
st.title("🥛 District Competitiveness Dashboard: Dairy Sector")
st.markdown("Explore the comparative advantage of districts in dairy manufacturing based on RCA × Index score.")

# File uploader (you can skip this if hardcoding the file)
uploaded_file = st.file_uploader("Upload the Combined RCA CSV File", type="csv")
if uploaded_file:
    df = pd.read_csv(uploaded_file)
else:
    df = pd.read_csv("lovable.csv")  # Use local CSV if deployed or no upload

# Sidebar filters
with st.sidebar:
    st.header("🔍 Filter Options")
    states = st.multiselect("Select State(s):", options=sorted(df['State'].dropna().unique()), default=[])
    rca_threshold = st.slider("Minimum RCA × Index Value:", min_value=0.0, max_value=10.0, value=4.0, step=0.1)

# Apply filters
filtered_df = df.copy()
if states:
    filtered_df = filtered_df[filtered_df['State'].isin(states)]
filtered_df = filtered_df[filtered_df['Combined Index'] >= rca_threshold]

# RCA formula explanation
st.markdown("""
### 🧮 RCA Definition

**Revealed Comparative Advantage (RCA)** is calculated as:


This dashboard multiplies RCA by a normalized index to sharpen competitiveness.

- **RCA × Index > 4** typically implies strong competitiveness in dairy.
""")

# Top Districts Table
st.markdown("### 🏆 Top Competitive Districts (Filtered)")
st.dataframe(filtered_df[['State', 'District', 'Combined Index', 'Outstanding Credit', 'Occupation/Activity']].sort_values(by='Combined Index', ascending=False), use_container_width=True)

# Bar chart
st.markdown("### 📊 RCA × Index by District")
fig = px.bar(filtered_df.sort_values(by='Combined Index', ascending=False).head(20),
             x='Combined Index',
             y='District',
             color='State',
             orientation='h',
             title="Top 20 Competitive Districts in Dairy Sector")
fig.update_layout(yaxis={'categoryorder':'total ascending'})
st.plotly_chart(fig, use_container_width=True)

# Top dairy industry for each district
st.markdown("### 🧀 Top Dairy Activity by District")
if 'Occupation/Activity' in filtered_df.columns:
    top_activities = filtered_df.groupby('District')['Occupation/Activity'].first().reset_index()
    st.dataframe(top_activities, use_container_width=True)
else:
    st.info("No Occupation/Activity column found in uploaded file.")

import pdfkit
import tempfile
import base64
from io import BytesIO

def convert_df_to_pdf(df, title="RCA District Report"):
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []

    # Title
    elements.append(Paragraph(title, styles['Title']))

    # Table
    data = [df.columns.tolist()] + df.values.tolist()
    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#e0e0e0')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 8),
        ('ALIGN', (0,0), (-1,-1), 'CENTER')
    ]))

    elements.append(table)
    doc.build(elements)
    buffer.seek(0)
    return buffer

st.markdown("---")
st.subheader("📄 Export Filtered Data as PDF")

if st.button("Export PDF"):
    pdf_file = convert_df_to_pdf(filtered_df)
    b64 = base64.b64encode(pdf_file.read()).decode()
    href = f'<a href="data:application/pdf;base64,{b64}" download="RCA_District_Report.pdf">📥 Download PDF</a>'
    st.markdown(href, unsafe_allow_html=True)


# Footer
st.markdown("""
---
🔗 **Created by Maitreyi Purohit**  
📊 **Source**: Y-Macro Analytics  
🏭 **Model**: District Competitiveness based on RCA × Index for Dairy Sector
""")

