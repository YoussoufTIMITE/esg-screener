"""
data_fetcher.py - Récupération des données financières et calcul des scores
Ce module utilise yfinance pour obtenir les données réelles et simule les scores ESG.
"""

import yfinance as yf
import pandas as pd
import random
from typing import Dict, Optional, Tuple
from dataclasses import dataclass


@dataclass
class FinancialData:
    """Structure de données pour les informations financières d'une entreprise."""
    symbol: str
    company_name: str
    sector: str
    industry: str
    debt_to_equity: Optional[float]
    free_cash_flow: Optional[float]
    current_price: Optional[float]
    market_cap: Optional[float]
    esg_score: float
    esg_environmental: float
    esg_social: float
    esg_governance: float
    verdict: str
    verdict_reasons: list


# Seuils pour le verdict d'investissement
THRESHOLDS = {
    "debt_to_equity_max": 2.0,      # Ratio D/E maximum acceptable
    "esg_score_min": 50.0,          # Score ESG minimum acceptable
    "free_cash_flow_min": 0,        # Cash flow minimum (positif requis)
}


def fetch_stock_data(symbol: str) -> Optional[Dict]:
    """
    Récupère les données boursières via yfinance.
    
    Args:
        symbol: Le symbole boursier (ex: AAPL, MSFT)
    
    Returns:
        Dictionnaire avec les données ou None si le symbole est invalide
    """
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        
        if not info or info.get("regularMarketPrice") is None:
            return None
        
        return info
    except Exception as e:
        print(f"Erreur lors de la récupération des données pour {symbol}: {e}")
        return None


def calculate_debt_to_equity(info: Dict) -> Optional[float]:
    """
    Calcule le ratio Dette/Equity à partir des données yfinance.
    
    Args:
        info: Dictionnaire des informations du ticker
    
    Returns:
        Le ratio D/E ou None si non disponible
    """
    total_debt = info.get("totalDebt")
    total_equity = info.get("totalStockholderEquity")
    
    if total_debt is not None and total_equity is not None and total_equity != 0:
        return round(total_debt / total_equity, 2)
    
    return info.get("debtToEquity")


def get_free_cash_flow(info: Dict) -> Optional[float]:
    """
    Récupère le Free Cash Flow depuis les données yfinance.
    
    Args:
        info: Dictionnaire des informations du ticker
    
    Returns:
        Le FCF ou None si non disponible
    """
    return info.get("freeCashflow")


def simulate_esg_score(sector: str = None) -> Tuple[float, float, float, float]:
    """
    Simule un score ESG réaliste basé sur le secteur d'activité.
    Les scores réels sont payants, donc nous simulons avec des valeurs cohérentes.
    
    Args:
        sector: Le secteur d'activité de l'entreprise
    
    Returns:
        Tuple (score_total, environmental, social, governance)
    """
    sector_base_scores = {
        "Technology": (65, 70, 60, 75),
        "Healthcare": (60, 55, 70, 65),
        "Financial Services": (55, 50, 60, 70),
        "Energy": (40, 35, 50, 55),
        "Consumer Cyclical": (55, 50, 60, 60),
        "Consumer Defensive": (60, 55, 65, 65),
        "Industrials": (50, 45, 55, 60),
        "Basic Materials": (45, 40, 50, 55),
        "Utilities": (55, 60, 50, 60),
        "Real Estate": (50, 55, 50, 55),
        "Communication Services": (60, 55, 65, 65),
    }
    
    base = sector_base_scores.get(sector, (55, 50, 55, 60))
    
    variation = lambda x: max(0, min(100, x + random.uniform(-10, 10)))
    
    environmental = round(variation(base[1]), 1)
    social = round(variation(base[2]), 1)
    governance = round(variation(base[3]), 1)
    
    total_score = round((environmental + social + governance) / 3, 1)
    
    return total_score, environmental, social, governance


def determine_verdict(
    debt_to_equity: Optional[float],
    free_cash_flow: Optional[float],
    esg_score: float
) -> Tuple[str, list]:
    """
    Détermine si une action est 'Investissable' ou 'Risqué' selon les critères définis.
    
    Args:
        debt_to_equity: Ratio Dette/Equity
        free_cash_flow: Cash flow libre
        esg_score: Score ESG
    
    Returns:
        Tuple (verdict, liste des raisons)
    """
    reasons = []
    is_risky = False
    
    if debt_to_equity is not None:
        if debt_to_equity > THRESHOLDS["debt_to_equity_max"]:
            is_risky = True
            reasons.append(f"Ratio D/E élevé ({debt_to_equity} > {THRESHOLDS['debt_to_equity_max']})")
        else:
            reasons.append(f"Ratio D/E acceptable ({debt_to_equity})")
    else:
        reasons.append("Ratio D/E non disponible")
    
    if free_cash_flow is not None:
        if free_cash_flow < THRESHOLDS["free_cash_flow_min"]:
            is_risky = True
            reasons.append(f"Cash flow négatif ({free_cash_flow:,.0f})")
        else:
            reasons.append(f"Cash flow positif ({free_cash_flow:,.0f})")
    else:
        reasons.append("Cash flow non disponible")
    
    if esg_score < THRESHOLDS["esg_score_min"]:
        is_risky = True
        reasons.append(f"Score ESG faible ({esg_score} < {THRESHOLDS['esg_score_min']})")
    else:
        reasons.append(f"Score ESG satisfaisant ({esg_score})")
    
    verdict = "Risqué" if is_risky else "Investissable"
    
    return verdict, reasons


def analyze_stock(symbol: str) -> Optional[FinancialData]:
    """
    Analyse complète d'une action : données financières + ESG + verdict.
    Fonction principale qui orchestre toutes les autres.
    
    Args:
        symbol: Le symbole boursier à analyser
    
    Returns:
        Objet FinancialData avec toutes les informations ou None si erreur
    """
    symbol = symbol.upper().strip()
    
    info = fetch_stock_data(symbol)
    if info is None:
        return None
    
    company_name = info.get("longName", info.get("shortName", symbol))
    sector = info.get("sector", "Unknown")
    industry = info.get("industry", "Unknown")
    current_price = info.get("currentPrice", info.get("regularMarketPrice"))
    market_cap = info.get("marketCap")
    
    debt_to_equity = calculate_debt_to_equity(info)
    free_cash_flow = get_free_cash_flow(info)
    
    esg_total, esg_env, esg_social, esg_gov = simulate_esg_score(sector)
    
    verdict, verdict_reasons = determine_verdict(debt_to_equity, free_cash_flow, esg_total)
    
    return FinancialData(
        symbol=symbol,
        company_name=company_name,
        sector=sector,
        industry=industry,
        debt_to_equity=debt_to_equity,
        free_cash_flow=free_cash_flow,
        current_price=current_price,
        market_cap=market_cap,
        esg_score=esg_total,
        esg_environmental=esg_env,
        esg_social=esg_social,
        esg_governance=esg_gov,
        verdict=verdict,
        verdict_reasons=verdict_reasons
    )


def format_large_number(value: Optional[float]) -> str:
    """
    Formate les grands nombres en format lisible (K, M, B).
    
    Args:
        value: La valeur numérique à formater
    
    Returns:
        Chaîne formatée
    """
    if value is None:
        return "N/A"
    
    abs_value = abs(value)
    sign = "-" if value < 0 else ""
    
    if abs_value >= 1e12:
        return f"{sign}{abs_value/1e12:.2f}T"
    elif abs_value >= 1e9:
        return f"{sign}{abs_value/1e9:.2f}B"
    elif abs_value >= 1e6:
        return f"{sign}{abs_value/1e6:.2f}M"
    elif abs_value >= 1e3:
        return f"{sign}{abs_value/1e3:.2f}K"
    else:
        return f"{sign}{abs_value:.2f}"


if __name__ == "__main__":
    test_symbols = ["AAPL", "MSFT", "GOOGL"]
    
    for sym in test_symbols:
        print(f"\n{'='*50}")
        print(f"Analyse de {sym}")
        print('='*50)
        
        result = analyze_stock(sym)
        
        if result:
            print(f"Entreprise: {result.company_name}")
            print(f"Secteur: {result.sector}")
            print(f"Ratio D/E: {result.debt_to_equity}")
            print(f"Free Cash Flow: {format_large_number(result.free_cash_flow)}")
            print(f"Score ESG: {result.esg_score}")
            print(f"Verdict: {result.verdict}")
        else:
            print("Impossible de récupérer les données")
