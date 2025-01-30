import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

RARITY_LEVELS = {
    "One Diamond": {"symbol": "💎", "name": "Comune", "value": 1},
    "Two Diamond": {"symbol": "💎💎", "name": "Non Comune", "value": 2},
    "Three Diamond": {"symbol": "💎💎💎", "name": "Raro", "value": 3},
    "Four Diamond": {"symbol": "💎💎💎💎", "name": "EX", "value": 4},
    "One Star": {"symbol": "⭐", "name": "Speciale", "value": 5}
}

MESSAGES = {
    'welcome': """
Benvenuto nel Bot di Scambio Pokémon TCGP! 🎮
Puoi utilizzare i seguenti comandi:
/offri - Offri una carta per lo scambio
/cerca - Cerca una carta
/lemiecarte - Visualizza le tue carte offerte
/lemiericerche - Visualizza le tue ricerche attive
/cartedisponibili - Visualizza tutte le carte scambiabili
/wanted - Visualizza tutte le carte ricercate
/matches - Visualizza i tuoi match attivi
/eliminaofferta - Elimina una tua offerta
/eliminaricerca - Elimina una tua ricerca
    """,
    'select_rarity': "Seleziona la rarità della carta:",
    'enter_card_name': "Inserisci il nome della carta:",
    'offer_saved': "La tua offerta è stata salvata con successo!",
    'search_saved': "La tua ricerca è stata salvata con successo!",
    'match_found': "È stata trovata una corrispondenza per la tua ricerca!"
}

COLLECTIONS = {
    'offers': 'offers',
    'searches': 'searches',
    'users': 'users'
}
