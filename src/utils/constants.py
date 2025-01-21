import os
from dotenv import load_dotenv

# Carica le variabili d'ambiente dal file .env
load_dotenv()

# Token del bot Telegram
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

# ID del progetto Google Cloud
PROJECT_ID = os.getenv('GOOGLE_CLOUD_PROJECT')

# Costanti per i livelli di rarità delle carte
RARITY_LEVELS = {
    "⬥": {"symbol": "⬥", "name": "Comune", "value": 1},
    "⬥⬥": {"symbol": "⬥⬥", "name": "Non Comune", "value": 2},
    "⬥⬥⬥": {"symbol": "⬥⬥⬥", "name": "Raro", "value": 3},
    "⬥⬥⬥⬥": {"symbol": "⬥⬥⬥⬥", "name": "EX", "value": 4},
    "★": {"symbol": "★", "name": "Speciale", "value": 5}
}

# Messaggi del bot
MESSAGES = {
    'welcome': """
Benvenuto nel Bot di Scambio Pokémon TCGP! 🎮

Puoi utilizzare i seguenti comandi:
/offri - Offri una carta per lo scambio
/cerca - Cerca una carta
/lemiecarte - Visualizza le tue carte offerte
/lemiericerche - Visualizza le tue ricerche attive
/cartedisponibili - Visualizza tutte le carte scambiabili
    """,
    'select_rarity': "Seleziona la rarità della carta:",
    'enter_card_name': "Inserisci il nome della carta:",
    'offer_saved': "La tua offerta è stata salvata con successo!",
    'search_saved': "La tua ricerca è stata salvata con successo!",
    'match_found': "È stata trovata una corrispondenza per la tua ricerca!"
}

# Configurazioni del database
COLLECTIONS = {
    'offers': 'offers',
    'searches': 'searches',
    'users': 'users'
}