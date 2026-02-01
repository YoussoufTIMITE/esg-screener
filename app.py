"""
app.py - Interface utilisateur Streamlit
Dashboard interactif pour l'ESG & Financial Screener.
"""

import streamlit as st
import pandas as pd
from datetime import datetime

from database import init_database, save_search, get_search_history, clear_history
from data_fetcher import analyze_stock, format_large_number, THRESHOLDS


# Configuration de la page Streamlit
st.set_page_config(
    page_title="ESG & Financial Screener",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)


def init_session_state():
    """Initialise les variables de session Streamlit."""
    if "last_analysis" not in st.session_state:
        st.session_state.last_analysis = None


def display_metric_card(label: str, value: str, delta: str = None, color: str = "normal"):
    """
    Affiche une métrique stylisée.
    
    Args:
        label: Le libellé de la métrique
        value: La valeur à afficher
        delta: Information complémentaire (optionnel)
        color: Couleur du texte ('normal', 'good', 'bad')
    """
    color_map = {
        "normal": "#FFFFFF",
        "good": "#00FF00",
        "bad": "#FF4444"
    }
    st.metric(label=label, value=value, delta=delta)


def display_esg_gauge(score: float, label: str):
    """
    Affiche une jauge de score ESG avec code couleur.
    
    Args:
        score: Le score (0-100)
        label: Le libellé de la jauge
    """
    if score >= 70:
        color = "#28a745"
        status = "Excellent"
    elif score >= 50:
        color = "#ffc107"
        status = "Moyen"
    else:
        color = "#dc3545"
        status = "Faible"
    
    st.markdown(f"""
    <div style="margin-bottom: 10px;">
        <p style="margin: 0; font-size: 14px;">{label}</p>
        <div style="background-color: #333; border-radius: 10px; height: 20px; width: 100%;">
            <div style="background-color: {color}; width: {score}%; height: 100%; border-radius: 10px; 
                        display: flex; align-items: center; justify-content: center;">
                <span style="color: white; font-size: 12px; font-weight: bold;">{score}</span>
            </div>
        </div>
        <p style="margin: 0; font-size: 12px; color: {color};">{status}</p>
    </div>
    """, unsafe_allow_html=True)


def display_verdict_banner(verdict: str, reasons: list):
    """
    Affiche une bannière colorée selon le verdict.
    
    Args:
        verdict: 'Investissable' ou 'Risqué'
        reasons: Liste des raisons du verdict
    """
    if verdict == "Investissable":
        bg_color = "#28a745"
        icon = "✅"
    else:
        bg_color = "#dc3545"
        icon = "⚠️"
    
    st.markdown(f"""
    <div style="background-color: {bg_color}; padding: 20px; border-radius: 10px; margin: 20px 0;">
        <h2 style="color: white; margin: 0; text-align: center;">{icon} Verdict: {verdict}</h2>
    </div>
    """, unsafe_allow_html=True)
    
    with st.expander("Voir les détails du verdict"):
        for reason in reasons:
            st.write(f"• {reason}")


def main():
    """Fonction principale de l'application Streamlit."""
    
    init_database()
    init_session_state()
    
    # Sidebar
    with st.sidebar:
        st.title("📊 ESG & Financial Screener")
        st.markdown("---")
        
        st.subheader("Rechercher une action")
        symbol_input = st.text_input(
            "Symbole boursier",
            placeholder="Ex: AAPL, MSFT, GOOGL",
            help="Entrez le ticker d'une action cotée"
        ).upper().strip()
        
        analyze_button = st.button("🔍 Analyser", type="primary", use_container_width=True)
        
        st.markdown("---")
        
        st.subheader("Seuils d'évaluation")
        st.caption(f"• Ratio D/E max: {THRESHOLDS['debt_to_equity_max']}")
        st.caption(f"• Score ESG min: {THRESHOLDS['esg_score_min']}")
        st.caption(f"• Cash flow: Positif requis")
        
        st.markdown("---")
        
        st.subheader("Actions rapides")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("AAPL", use_container_width=True):
                symbol_input = "AAPL"
                analyze_button = True
        with col2:
            if st.button("MSFT", use_container_width=True):
                symbol_input = "MSFT"
                analyze_button = True
        
        col3, col4 = st.columns(2)
        with col3:
            if st.button("GOOGL", use_container_width=True):
                symbol_input = "GOOGL"
                analyze_button = True
        with col4:
            if st.button("TSLA", use_container_width=True):
                symbol_input = "TSLA"
                analyze_button = True
    
    # Contenu principal
    st.title("ESG & Financial Screener")
    st.markdown("Analysez les ratios financiers et le score ESG de n'importe quelle action cotée.")
    
    # Tabs principales
    tab1, tab2 = st.tabs(["📈 Analyse", "📜 Historique"])
    
    with tab1:
        if analyze_button and symbol_input:
            with st.spinner(f"Analyse de {symbol_input} en cours..."):
                result = analyze_stock(symbol_input)
            
            if result:
                st.session_state.last_analysis = result
                
                save_search(
                    symbol=result.symbol,
                    company_name=result.company_name,
                    debt_to_equity=result.debt_to_equity,
                    free_cash_flow=result.free_cash_flow,
                    esg_score=result.esg_score,
                    verdict=result.verdict
                )
                
                # Header avec info entreprise
                st.header(f"{result.company_name} ({result.symbol})")
                st.caption(f"Secteur: {result.sector} | Industrie: {result.industry}")
                
                # Verdict
                display_verdict_banner(result.verdict, result.verdict_reasons)
                
                # Métriques principales
                st.subheader("📊 Ratios Financiers")
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    de_value = result.debt_to_equity if result.debt_to_equity else "N/A"
                    de_status = "⚠️ Élevé" if result.debt_to_equity and result.debt_to_equity > THRESHOLDS["debt_to_equity_max"] else "✅ OK" if result.debt_to_equity else None
                    st.metric("Ratio Dette/Equity", de_value, de_status)
                
                with col2:
                    fcf_value = format_large_number(result.free_cash_flow)
                    fcf_status = "⚠️ Négatif" if result.free_cash_flow and result.free_cash_flow < 0 else "✅ Positif" if result.free_cash_flow else None
                    st.metric("Free Cash Flow", fcf_value, fcf_status)
                
                with col3:
                    price_value = f"${result.current_price:.2f}" if result.current_price else "N/A"
                    st.metric("Prix actuel", price_value)
                
                with col4:
                    mcap_value = format_large_number(result.market_cap)
                    st.metric("Market Cap", mcap_value)
                
                # Scores ESG
                st.subheader("🌱 Scores ESG (Simulés)")
                st.caption("Note: Les scores ESG sont simulés car les API réelles sont payantes.")
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.markdown("### Score Global")
                    display_esg_gauge(result.esg_score, "ESG Total")
                
                with col2:
                    display_esg_gauge(result.esg_environmental, "🌍 Environnemental")
                
                with col3:
                    display_esg_gauge(result.esg_social, "👥 Social")
                
                with col4:
                    display_esg_gauge(result.esg_governance, "🏛️ Gouvernance")
                
                # Résumé en DataFrame
                st.subheader("📋 Résumé")
                summary_data = {
                    "Métrique": ["Symbole", "Entreprise", "Secteur", "Ratio D/E", "Free Cash Flow", "Score ESG", "Verdict"],
                    "Valeur": [
                        result.symbol,
                        result.company_name,
                        result.sector,
                        str(result.debt_to_equity) if result.debt_to_equity else "N/A",
                        format_large_number(result.free_cash_flow),
                        str(result.esg_score),
                        result.verdict
                    ]
                }
                st.dataframe(pd.DataFrame(summary_data), use_container_width=True, hide_index=True)
                
            else:
                st.error(f"❌ Impossible de trouver des données pour le symbole '{symbol_input}'. Vérifiez que le ticker est correct.")
        
        elif analyze_button and not symbol_input:
            st.warning("⚠️ Veuillez entrer un symbole boursier.")
        
        else:
            st.info("👈 Entrez un symbole boursier dans la barre latérale pour commencer l'analyse.")
            
            st.markdown("""
            ### Comment utiliser cette application ?
            
            1. **Entrez un symbole boursier** (ex: AAPL pour Apple, MSFT pour Microsoft)
            2. **Cliquez sur Analyser** pour obtenir les données
            3. **Consultez les résultats** : ratios financiers, score ESG et verdict
            
            ### Critères d'évaluation
            
            Une action est considérée **Investissable** si :
            - Le ratio Dette/Equity est inférieur à 2.0
            - Le Free Cash Flow est positif
            - Le score ESG est supérieur à 50
            
            Si un de ces critères n'est pas respecté, l'action est marquée comme **Risqué**.
            """)
    
    with tab2:
        st.header("📜 Historique des recherches")
        
        history = get_search_history(limit=50)
        
        if history:
            col1, col2 = st.columns([3, 1])
            with col2:
                if st.button("🗑️ Effacer l'historique", type="secondary"):
                    deleted = clear_history()
                    st.success(f"{deleted} enregistrement(s) supprimé(s).")
                    st.rerun()
            
            history_data = []
            for row in history:
                history_data.append({
                    "Date": row[6][:19] if row[6] else "N/A",
                    "Symbole": row[0],
                    "Entreprise": row[1],
                    "D/E": row[2] if row[2] else "N/A",
                    "FCF": format_large_number(row[3]) if row[3] else "N/A",
                    "ESG": row[4],
                    "Verdict": row[5]
                })
            
            df_history = pd.DataFrame(history_data)
            
            def color_verdict(val):
                if val == "Investissable":
                    return "background-color: #28a745; color: white"
                elif val == "Risqué":
                    return "background-color: #dc3545; color: white"
                return ""
            
            styled_df = df_history.style.applymap(color_verdict, subset=["Verdict"])
            st.dataframe(styled_df, use_container_width=True, hide_index=True)
            
            st.subheader("📊 Statistiques")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total recherches", len(history_data))
            
            with col2:
                investissables = sum(1 for h in history_data if h["Verdict"] == "Investissable")
                st.metric("Investissables", investissables)
            
            with col3:
                risques = sum(1 for h in history_data if h["Verdict"] == "Risqué")
                st.metric("Risqués", risques)
        else:
            st.info("Aucune recherche dans l'historique. Commencez par analyser une action!")
    
    # Footer
    st.markdown("---")
    st.caption("ESG & Financial Screener | Données financières via yfinance | Scores ESG simulés")


if __name__ == "__main__":
    main()
