"""
database.py - Gestion de la base de données SQLite
Ce module gère la connexion à SQLite et les opérations CRUD pour l'historique des recherches.
"""

import sqlite3
from datetime import datetime
from typing import List, Tuple, Optional

DATABASE_NAME = "data.db"


def get_connection() -> sqlite3.Connection:
    """
    Établit une connexion à la base de données SQLite.
    Retourne un objet Connection.
    """
    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def init_database() -> None:
    """
    Initialise la base de données en créant la table 'search_history' si elle n'existe pas.
    Cette table stocke l'historique de toutes les recherches effectuées par les utilisateurs.
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS search_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol VARCHAR(10) NOT NULL,
            company_name VARCHAR(255),
            debt_to_equity REAL,
            free_cash_flow REAL,
            esg_score REAL,
            verdict VARCHAR(20),
            search_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    conn.close()


def save_search(
    symbol: str,
    company_name: str,
    debt_to_equity: Optional[float],
    free_cash_flow: Optional[float],
    esg_score: float,
    verdict: str
) -> int:
    """
    Enregistre une nouvelle recherche dans l'historique.
    
    Args:
        symbol: Le symbole boursier (ex: AAPL)
        company_name: Le nom complet de l'entreprise
        debt_to_equity: Ratio Dette/Equity
        free_cash_flow: Cash flow libre
        esg_score: Score ESG simulé
        verdict: 'Investissable' ou 'Risqué'
    
    Returns:
        L'ID de l'enregistrement créé
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO search_history 
        (symbol, company_name, debt_to_equity, free_cash_flow, esg_score, verdict, search_date)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (symbol, company_name, debt_to_equity, free_cash_flow, esg_score, verdict, datetime.now()))
    
    conn.commit()
    last_id = cursor.lastrowid
    conn.close()
    
    return last_id


def get_search_history(limit: int = 50) -> List[Tuple]:
    """
    Récupère l'historique des recherches, triées par date décroissante.
    
    Args:
        limit: Nombre maximum d'enregistrements à retourner (défaut: 50)
    
    Returns:
        Liste des recherches sous forme de tuples
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT symbol, company_name, debt_to_equity, free_cash_flow, 
               esg_score, verdict, search_date
        FROM search_history
        ORDER BY search_date DESC
        LIMIT ?
    """, (limit,))
    
    results = cursor.fetchall()
    conn.close()
    
    return results


def get_symbol_stats(symbol: str) -> Optional[dict]:
    """
    Récupère les statistiques d'un symbole spécifique (dernière recherche).
    
    Args:
        symbol: Le symbole boursier à rechercher
    
    Returns:
        Dictionnaire avec les données ou None si non trouvé
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT * FROM search_history
        WHERE symbol = ?
        ORDER BY search_date DESC
        LIMIT 1
    """, (symbol.upper(),))
    
    result = cursor.fetchone()
    conn.close()
    
    if result:
        return dict(result)
    return None


def clear_history() -> int:
    """
    Supprime tout l'historique des recherches.
    
    Returns:
        Nombre d'enregistrements supprimés
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM search_history")
    count = cursor.fetchone()[0]
    
    cursor.execute("DELETE FROM search_history")
    
    conn.commit()
    conn.close()
    
    return count


if __name__ == "__main__":
    init_database()
    print("Base de données initialisée avec succès!")
