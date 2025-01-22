from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from utils.constants import RARITY_LEVELS

def get_rarity_keyboard(action_prefix: str) -> InlineKeyboardMarkup:
    """
    Crea una tastiera inline con i livelli di rarità.
    
    Args:
        action_prefix: Prefisso per la callback_data ('offer' o 'search')
        
    Returns:
        InlineKeyboardMarkup: Tastiera con i bottoni per le rarità
    """
    # Creiamo una lista di bottoni, due per riga
    keyboard = []
    current_row = []
    
    for rarity, info in RARITY_LEVELS.items():
        # Creiamo un bottone con il simbolo della rarità e una descrizione
        button = InlineKeyboardButton(
            f"{info['symbol']} - {info['name']}", 
            callback_data=f"{action_prefix}_rarity_{rarity}"
        )
        
        current_row.append(button)
        
        # Ogni due bottoni, creiamo una nuova riga
        if len(current_row) == 2:
            keyboard.append(current_row)
            current_row = []
    
    # Se c'è un bottone rimasto, lo aggiungiamo all'ultima riga
    if current_row:
        keyboard.append(current_row)
    
    return InlineKeyboardMarkup(keyboard)

def get_confirmation_keyboard(action: str, item_id: str) -> InlineKeyboardMarkup:
    """
    Crea una tastiera per confermare o annullare un'azione.
    
    Args:
        action: Tipo di azione ('offer' o 'search')
        item_id: ID dell'elemento nel database
        
    Returns:
        InlineKeyboardMarkup: Tastiera con bottoni di conferma e annulla
    """
    keyboard = [[
        InlineKeyboardButton("✅ Conferma", callback_data=f"confirm_{action}_{item_id}"),
        InlineKeyboardButton("❌ Annulla", callback_data=f"cancel_{action}_{item_id}")
    ]]
    return InlineKeyboardMarkup(keyboard)

def get_my_items_keyboard(items: list, action: str) -> InlineKeyboardMarkup:
    """
    Crea una tastiera con la lista delle carte offerte o cercate dall'utente.
    
    Args:
        items: Lista di dizionari contenenti le informazioni delle carte
        action: Tipo di azione ('offer' o 'search')
        
    Returns:
        InlineKeyboardMarkup: Tastiera con la lista delle carte
    """
    keyboard = []
    
    for item in items:
        # Per ogni carta, creiamo un bottone con nome e rarità
        button_text = f"{item['card_name']} {RARITY_LEVELS[item['rarity']]['symbol']}"
        callback_data = f"view_{action}_{item['id']}"
        keyboard.append([InlineKeyboardButton(button_text, callback_data=callback_data)])
    
    # Aggiungiamo un bottone per tornare indietro
    keyboard.append([InlineKeyboardButton("🔙 Indietro", callback_data="back_to_main")])
    
    return InlineKeyboardMarkup(keyboard)