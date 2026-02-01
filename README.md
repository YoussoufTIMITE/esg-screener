# 📊 ESG & Financial Screener

## 📝 Description du Projet
Application d'aide à la décision pour investisseurs éthiques. Cet outil permet d'analyser instantanément la santé financière et le profil ESG (Environnement, Social, Gouvernance) d'entreprises cotées en bourse.

L'objectif est de démontrer comment automatiser l'analyse fondamentale (Ratios D/E, Cash Flow) tout en intégrant des critères extra-financiers.

## 🚀 Fonctionnalités
- **Live Data :** Récupération en temps réel des données financières via l'API Yahoo Finance.
- **Scoring ESG :** Algorithme de simulation de notation basé sur les moyennes sectorielles.
- **Persistance des données :** Sauvegarde automatique de l'historique des recherches dans une base SQL locale.
- **Verdict Intelligent :** Système de règles métier pour classer automatiquement une action comme "Investissable" ou "Risquée".

## 🛠 Stack Technique
Ce projet a été construit avec une approche **Clean Architecture** et modulaire :

* **Langage :** Python 3.9+
* **Interface (Frontend) :** Streamlit
* **Data Processing :** Pandas & NumPy
* **Base de Données :** SQLite (SQL natif, pas d'ORM pour la performance)
* **API Externe :** yfinance

## 📂 Structure du Code (Architecture MVC)
* `app.py` (View) : Gère l'interface utilisateur et l'état de la session.
* `data_fetcher.py` (Controller/Logic) : Contient la logique métier, les appels API et le calcul des scores.
* `database.py` (Model) : Gère les connexions SQL et les transactions CRUD.

## 📦 Installation & Lancement

1. Cloner le repo :
```bash
git clone [https://github.com/VOTRE_NOM_UTILISATEUR/esg-screener.git](https://github.com/VOTRE_NOM_UTILISATEUR/esg-screener.git)