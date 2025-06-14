from datetime import date, timedelta
import yfinance as yf
import plotly.graph_objects as go
import streamlit as st
import pandas as pd

# Configuration de la page Streamlit
st.set_page_config(layout="wide")
st.title("Dashboard Boursier")

# Sidebar pour les options
st.sidebar.title('Options')
start_date = "2020-05-25"
today = date.today() + timedelta(days=1)
end_date = today.strftime("%Y-%m-%d")

# Charger les données boursières
def load_data(ticker, start_date, end_date):
    data = yf.download(ticker, start=start_date, end=end_date)
    if data.empty:
        st.warning(f"Les données pour {ticker} n'ont pas pu être récupérées.")
    else:
        data['Date'] = data.index
    return data

# Liste des symboles boursiers disponibles
symbols = {
    'Bitcoin': 'BTC-USD',
    'Ethereum': 'ETH-USD',
    'Apple': 'AAPL',
    'Microsoft': 'MSFT',
    'Intel': 'INTC',
    'Tesla': 'TSLA',
    'Gold': 'GC=F',
    'Google': 'GOOG',
    'Nintendo': 'NTDOY',
}

# Initialisation des clés dans st.session_state
for i in range(4):
    if f'symbol_{i}' not in st.session_state:
        st.session_state[f'symbol_{i}'] = list(symbols.keys())[0]

# Création des widgets selectbox
selected_symbols = []
for i in range(4):
    selected_symbols.append(st.sidebar.selectbox(
        f'Choisissez un {i+1}er cours',
        list(symbols.keys()),
        key=f'symbol_{i}'
    ))

# Supprimer les entrées vides et doublons
selected_symbols = [symbol for symbol in selected_symbols if symbol]
selected_symbols = list(set(selected_symbols))

# Charger les données pour les symboles sélectionnés
data = {}
for symbol in selected_symbols:
    try:
        data[symbol] = load_data(symbols[symbol], start_date, end_date)
    except Exception as e:
        st.error(f"Erreur lors du téléchargement des données pour {symbol}: {e}")

# Afficher les données brutes pour vérification
for symbol in selected_symbols:
    st.write(f"Données pour {symbol}:")
    st.write(data[symbol].head())

# Générer un graphique simplifié pour chaque symbole
st.subheader('Cours des actions sélectionnées')
for symbol in selected_symbols:
    df = data.get(symbol, pd.DataFrame())
    if df.empty:
        st.warning(f"Aucune donnée disponible pour {symbol}.")
    else:
        # Vérification des colonnes disponibles
        st.write(f"Colonnes disponibles pour {symbol}: {df.columns}")

        # Vérifier et nettoyer les données
        df['Date'] = pd.to_datetime(df['Date'])

        # Accès à la colonne "Close" avec MultiIndex
        try:
            close_col = df[('Close', symbols[symbol])]
        except KeyError:
            st.warning(f"Impossible de trouver la colonne 'Close' pour {symbol}.")
            continue

        # Vérifiez si la colonne Close contient des valeurs valides
        if close_col.isnull().all():
            st.warning(f"La colonne 'Close' pour {symbol} ne contient aucune donnée valide.")
        else:
            # Générer le graphique
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df['Date'],
                y=close_col,
                mode='lines',
                name='Close Price',
                line=dict(color='blue', width=1)
            ))
            fig.update_layout(
                title=f"Cours de {symbol}",
                xaxis_title='Date',
                yaxis_title='Close Price',
                template='simple_white'
            )
            st.plotly_chart(fig)
