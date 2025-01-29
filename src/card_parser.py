import os
import re
import sys
sys.path.append("/home/dietpi/Desktop/s.monti-s.cambi/src")
from database.database import Database  # import corretto dal package

# Mapping delle rarità
RARITY_ICONS = {
    "One Diamond": "💎",
    "Two Diamond": "💎💎",
    "Three Diamond": "💎💎💎",
    "Four Diamond": "💎💎💎💎",
    "One Star": "⭐"
}

# Ordine di visualizzazione delle rarità
RARITY_ORDER = [
    "One Diamond",
    "Two Diamond", 
    "Three Diamond",
    "Four Diamond",
    "One Star"
]

class CardParser:
    def __init__(self):
        self.db = Database()
        
    def parse_ts_file(self, file_path: str) -> dict:
        """Estrae nome e rarità da un file di carta Pokemon."""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
            name_match = re.search(r'name:\s*{\s*en:\s*"([^"]+)"', content)
            rarity_match = re.search(r'rarity:\s*"([^"]+)"', content)
            
            if name_match and rarity_match:
                rarity = rarity_match.group(1)
                if rarity in RARITY_ICONS:  # Verifica che la rarità sia valida
                    return {
                        'name': name_match.group(1),
                        'rarity': rarity,
                        'rarity_icon': RARITY_ICONS[rarity]
                    }
            return None

async def load_cards_to_db(repo_path: str, sets: list):
    """Carica le carte nel database dai set specificati."""
    parser = CardParser()
    
    for set_name in sets:
        set_path = os.path.join(repo_path, set_name.lower())
        if os.path.isdir(set_path):
            print(f"Processando set: {set_name}")
            
            # Aggiungi il set
            await parser.db.add_set(set_name, set_name.lower())
            
            # Processa ogni file .ts nella directory
            for file_name in os.listdir(set_path):
                if file_name.endswith('.ts') and file_name != 'index.ts':
                    try:
                        card_data = parser.parse_ts_file(os.path.join(set_path, file_name))
                        if card_data:
                            await parser.db.add_card(
                                set_code=set_name.lower(),
                                card_name=card_data['name'],
                                rarity=card_data['rarity'],
                                rarity_icon=card_data['rarity_icon']
                            )
                            print(f"Aggiunta: {card_data['name']} {card_data['rarity_icon']}")
                    except Exception as e:
                        print(f"Errore con {file_name}: {str(e)}")

if __name__ == "__main__":
    import asyncio
    
    REPO_PATH = "/home/dietpi/Desktop/ptcgp-card-db"
    SETS = ["genetic_apex", "mythical_island"]
    
    asyncio.run(load_cards_to_db(REPO_PATH, SETS))
