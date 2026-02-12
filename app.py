import streamlit as st
import pandas as pd
import io
from parser import load_data, process_leave_data
from visualizer import create_gantt_chart

st.set_page_config(page_title="Générateur de Planning Congés", layout="wide")

st.title("Générateur de Planning de Congés")
st.markdown("""
Transformez votre tableau Excel/CSV/Google Sheets en un calendrier PDF visuel.
""")

# Input section
st.sidebar.header("Source de Données")

# Template download
with open("template.xlsx", "rb") as file:
    st.sidebar.download_button(
        label="📥 Télécharger le modèle Excel",
        data=file,
        file_name="modele_conges.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        help="Modèle Excel avec exemples de couleurs et instructions."
    )
st.sidebar.markdown("---")

input_method = st.sidebar.radio("Choisir la méthode d'import :", ("Fichier (Excel/CSV)", "Lien Google Sheets"))

df_raw = None

try:
    if input_method == "Fichier (Excel/CSV)":
        uploaded_file = st.sidebar.file_uploader("Téléverser un fichier", type=["csv", "xlsx"])
        if uploaded_file:
            df_raw = load_data(uploaded_file)
            
    else:
        sheet_url = st.sidebar.text_input("Coller le lien Google Sheets :", 
                                          placeholder="https://docs.google.com/spreadsheets/...")
        if sheet_url:
            df_raw = load_data(sheet_url)

    if df_raw is not None:
        st.subheader("Aperçu des Données")
        st.dataframe(df_raw.head())
        
        # Process data
        with st.spinner("Traitement des données..."):
            df_leaves = process_leave_data(df_raw)
        
        if not df_leaves.empty:
            st.subheader("Calendrier Généré")
            
            # Create chart
            fig = create_gantt_chart(df_leaves)
            st.pyplot(fig)
            
            # Save to buffer for download
            pdf_buffer = io.BytesIO()
            fig.savefig(pdf_buffer, format='pdf', bbox_inches='tight')
            pdf_buffer.seek(0)
            
            st.download_button(
                label="Télécharger le Planning en PDF",
                data=pdf_buffer,
                file_name="planning_conges.pdf",
                mime="application/pdf"
            )
        else:
            st.warning("Aucune donnée de congé valide n'a été trouvée. Vérifiez le format (ex: 'Du 14/05/25 au 17/05/25').")

except Exception as e:
    st.error(f"Une erreur est survenue : {e}")
    if "Google Sheets" in str(e) or "401" in str(e):
        with st.expander("Comment corriger l'erreur Google Sheets ?"):
            st.markdown("""
            **Le lien n'est pas accessible directement.**
            1. Ouvrez votre Google Sheet.
            2. Allez dans **Fichier** > **Partager** > **Publier sur le web**.
            3. Changez "Page Web" par **Valeurs séparées par des virgules (.csv)**.
            4. Copiez le lien généré et collez-le ci-dessus.
            """)

st.markdown("---")
st.markdown("*Note : Le format attendu pour les cellules est 'Du DD/MM/YY au DD/MM/YY'.*")
