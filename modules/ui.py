import streamlit as st

def inject_global_styles():
    """Injecte le style CSS global pour l'application."""
    st.markdown("""<style>
/* Reset et polices - Cibler spécifiquement sans casser les icônes Material */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body {
    font-family: 'Inter', sans-serif;
}

/* Fond global */
.stApp {
    background-color: #0f172a;
    background-image: 
        radial-gradient(at 0% 0%, rgba(139, 92, 246, 0.15) 0px, transparent 50%),
        radial-gradient(at 100% 100%, rgba(236, 72, 153, 0.1) 0px, transparent 50%);
    color: #f8fafc;
}

/* Header Styling */
.main-header {
    background: rgba(255, 255, 255, 0.03);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 16px;
    padding: 0.75rem 2rem;
    margin-bottom: 1rem;
    text-align: center;
    box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3);
}
.gradient-text {
    background: linear-gradient(90deg, #8b5cf6, #ec4899);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-weight: 800;
    font-size: 2rem;
    margin-bottom: 0.1rem;
}

/* Stats Cards */
.stat-card {
    background: rgba(255, 255, 255, 0.03);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 16px;
    padding: 1.25rem 0.5rem;
    text-align: center;
    box-shadow: 0 10px 20px -5px rgba(0, 0, 0, 0.3);
    transition: transform 0.3s ease, border 0.3s ease;
    display: flex;
    flex-direction: column;
    justify-content: center;
    min-height: 150px;
}
.stat-card:hover {
    transform: translateY(-5px);
    border: 1px solid rgba(139, 92, 246, 0.4);
}
.stat-card .value {
    font-size: 2rem;
    font-weight: 800;
    background: linear-gradient(90deg, #8b5cf6, #ec4899);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0.5rem;
}
.stat-card .label {
    font-size: 0.9rem;
    color: #cbd5e1;
    font-weight: 600;
    letter-spacing: 0.02em;
    text-transform: uppercase;
}

/* Cards & Containers */
div[data-testid="stExpander"] {
    background: rgba(30, 41, 59, 0.5) !important;
    border: 1px solid rgba(255, 255, 255, 0.05) !important;
    border-radius: 16px !important;
}

/* Eviter d'affecter le file uploader - cibles spécifiques */
button[kind="primary"] {
    background: linear-gradient(90deg, #7c3aed, #db2777) !important;
    border: none !important;
    color: white !important;
    border-radius: 12px !important;
    font-weight: 600 !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 4px 15px rgba(124, 58, 237, 0.25) !important;
}
button[kind="primary"]:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(124, 58, 237, 0.4) !important;
}

/* Dataframe Styling */
div[data-testid="stDataFrame"] {
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    border-radius: 16px !important;
    padding: 10px;
    background: rgba(15, 23, 42, 0.8) !important;
}

/* Inputs (Texte seulement) */
div[data-testid="stTextInput"] input {
    background: rgba(0, 0, 0, 0.2) !important;
    border-radius: 10px !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    color: white !important;
}
div[data-testid="stTextInput"] input:focus {
    border: 1px solid #8b5cf6 !important;
    box-shadow: 0 0 0 2px rgba(139, 92, 246, 0.2) !important;
}
</style>""", unsafe_allow_html=True)

def render_main_header():
    """Affiche le grand titre principal (header) de l'application."""
    st.markdown(
        """
        <div class="main-header">
            <h1 class="gradient-text">OdooExcelCleaner</h1>
            <p style="color: #94a3b8; font-size: 1.2rem; margin-top: 0.5rem;">Traitement de données haute performance</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
