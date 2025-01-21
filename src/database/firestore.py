import os
import logging
from google.cloud import firestore
from google.oauth2 import service_account
from src.utils.constants import COLLECTIONS, PROJECT_ID
from google.cloud.firestore_v1.base_query import FieldFilter

# Configurazione del logging per tracciare le operazioni del database
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

class Database:
    def __init__(self):
        """
        Inizializza la connessione al database Firestore.
        Questa classe gestisce tutte le operazioni di database per il bot,
        incluse le operazioni di lettura e scrittura per offerte e ricerche.
        """
        try:
            credentials_path = "/app/service-account-key.json"
            logging.info(f"Initializing Firestore with project ID: {PROJECT_ID}")
            
            if os.path.exists(credentials_path):
                credentials = service_account.Credentials.from_service_account_file(credentials_path)
                self.db = firestore.Client(
                    project=PROJECT_ID,
                    credentials=credentials
                )
            else:
                self.db = firestore.Client(project=PROJECT_ID)
            
            logging.info("Firestore client initialized successfully")
            
        except Exception as e:
            logging.error(f"Error initializing Firestore: {str(e)}")
            raise

    async def save_user(self, user_data: dict):
        """
        Salva o aggiorna le informazioni dell'utente nel database.
        
        Args:
            user_data: Dizionario contenente i dati dell'utente da salvare
        """
        try:
            user_ref = self.db.collection(COLLECTIONS['users']).document(str(user_data['id']))
            user_ref.set(user_data, merge=True)
            logging.info(f"Saved/updated user {user_data['id']}")
        except Exception as e:
            logging.error(f"Error saving user: {str(e)}")
            raise

    async def get_user_info(self, user_id: int) -> dict:
        """
        Recupera le informazioni di un utente dal database.
        
        Args:
            user_id: ID dell'utente Telegram
            
        Returns:
            dict: Dati dell'utente o None se non trovato
        """
        try:
            user_ref = self.db.collection(COLLECTIONS['users']).document(str(user_id))
            user = user_ref.get()
            return user.to_dict() if user.exists else None
        except Exception as e:
            logging.error(f"Error getting user info: {str(e)}")
            raise

    async def save_offer(self, user_id: int, card_name: str, rarity: str) -> str:
        """
        Salva una nuova offerta di carta nel database.
        
        Args:
            user_id: ID dell'utente Telegram che offre la carta
            card_name: Nome della carta Pokémon
            rarity: Livello di rarità della carta
            
        Returns:
            str: ID del documento creato
        """
        try:
            offer_ref = self.db.collection(COLLECTIONS['offers']).document()
            offer_data = {
                'user_id': user_id,
                'card_name': card_name.lower(),
                'rarity': rarity,
                'timestamp': firestore.SERVER_TIMESTAMP
            }
            
            offer_ref.set(offer_data)
            logging.info(f"Saved offer for card {card_name} with ID {offer_ref.id}")
            return offer_ref.id
        except Exception as e:
            logging.error(f"Error saving offer: {str(e)}")
            raise

    async def save_search(self, user_id: int, card_name: str, rarity: str) -> str:
        """
        Salva una nuova ricerca di carta nel database.
        
        Args:
            user_id: ID dell'utente Telegram che cerca la carta
            card_name: Nome della carta Pokémon
            rarity: Livello di rarità della carta
            
        Returns:
            str: ID del documento creato
        """
        try:
            search_ref = self.db.collection(COLLECTIONS['searches']).document()
            search_data = {
                'user_id': user_id,
                'card_name': card_name.lower(),
                'rarity': rarity,
                'timestamp': firestore.SERVER_TIMESTAMP
            }
            
            search_ref.set(search_data)
            logging.info(f"Saved search for card {card_name} with ID {search_ref.id}")
            return search_ref.id
        except Exception as e:
            logging.error(f"Error saving search: {str(e)}")
            raise

    async def get_user_offers(self, user_id: int) -> list:
        """
        Recupera tutte le offerte di un utente specifico.
        
        Args:
            user_id: ID dell'utente Telegram
            
        Returns:
            list: Lista delle offerte dell'utente
        """
        try:
            # Utilizziamo FieldFilter per una query più precisa
            field_filter = FieldFilter("user_id", "==", user_id)
            offers = self.db.collection(COLLECTIONS['offers']).where(filter=field_filter).stream()
            return [offer.to_dict() for offer in offers]
        except Exception as e:
            logging.error(f"Error getting user offers: {str(e)}")
            raise

    async def get_user_searches(self, user_id: int) -> list:
        """
        Recupera tutte le ricerche di un utente specifico.
        
        Args:
            user_id: ID dell'utente Telegram
            
        Returns:
            list: Lista delle ricerche dell'utente
        """
        try:
            field_filter = FieldFilter("user_id", "==", user_id)
            searches = self.db.collection(COLLECTIONS['searches']).where(filter=field_filter).stream()
            return [search.to_dict() for search in searches]
        except Exception as e:
            logging.error(f"Error getting user searches: {str(e)}")
            raise

    async def find_matching_searches(self, card_name: str, rarity: str) -> list:
        """
        Trova le ricerche che corrispondono a una carta offerta.
        
        Args:
            card_name: Nome della carta
            rarity: Rarità della carta
            
        Returns:
            list: Lista delle ricerche corrispondenti
        """
        try:
            name_filter = FieldFilter("card_name", "==", card_name.lower())
            rarity_filter = FieldFilter("rarity", "==", rarity)
            
            searches = (self.db.collection(COLLECTIONS['searches'])
                       .where(filter=name_filter)
                       .where(filter=rarity_filter)
                       .stream())
            
            return [search.to_dict() for search in searches]
        except Exception as e:
            logging.error(f"Error finding matching searches: {str(e)}")
            raise

    async def find_matching_offers(self, card_name: str, rarity: str) -> list:
        """
        Trova le offerte che corrispondono a una ricerca.
        
        Args:
            card_name: Nome della carta
            rarity: Rarità della carta
            
        Returns:
            list: Lista delle offerte corrispondenti
        """
        try:
            name_filter = FieldFilter("card_name", "==", card_name.lower())
            rarity_filter = FieldFilter("rarity", "==", rarity)
            
            offers = (self.db.collection(COLLECTIONS['offers'])
                     .where(filter=name_filter)
                     .where(filter=rarity_filter)
                     .stream())
            
            return [offer.to_dict() for offer in offers]
        except Exception as e:
            logging.error(f"Error finding matching offers: {str(e)}")
            raise

    async def get_all_cards(self) -> list:
        """
        Recupera e organizza tutte le carte disponibili con le informazioni degli utenti.
        Aggrega le offerte multiple della stessa carta e ordina alfabeticamente.
        
        Returns:
            list: Lista di dizionari dove ogni dizionario contiene:
                - card_name: Nome della carta
                - rarity: Livello di rarità
                - users: Lista di utenti che offrono la carta
        """
        try:
            offers = self.db.collection(COLLECTIONS['offers']).stream()
            # Dizionario per aggregare le offerte della stessa carta
            cards_dict = {}
            
            for offer in offers:
                offer_data = offer.to_dict()
                user_info = await self.get_user_info(offer_data['user_id'])
                
                # Creiamo una chiave unica per ogni combinazione carta/rarità
                card_key = f"{offer_data['card_name']}_{offer_data['rarity']}"
                
                # Prepariamo le informazioni dell'utente
                user_display = None
                if user_info:
                    user_display = f"@{user_info['username']}" if user_info.get('username') else user_info.get('first_name', f"User_{offer_data['user_id']}")
                else:
                    user_display = f"User_{offer_data['user_id']}"
                
                # Aggiungiamo o aggiorniamo l'entry nel dizionario
                if card_key not in cards_dict:
                    cards_dict[card_key] = {
                        'card_name': offer_data['card_name'],
                        'rarity': offer_data['rarity'],
                        'users': [user_display]
                    }
                else:
                    # Aggiungiamo l'utente solo se non è già presente
                    if user_display not in cards_dict[card_key]['users']:
                        cards_dict[card_key]['users'].append(user_display)
            
            # Convertiamo il dizionario in lista e ordiniamo alfabeticamente
            result = list(cards_dict.values())
            result.sort(key=lambda x: x['card_name'].lower())
            
            return result
        except Exception as e:
            logging.error(f"Error getting all cards: {str(e)}")
            raise

    async def check_existing_card(self, card_name: str, rarity: str) -> list:
        """
        Controlla se una carta esiste già nel database.
        
        Args:
            card_name: Nome della carta da cercare
            rarity: Rarità della carta
            
        Returns:
            list: Lista delle offerte esistenti per quella carta
        """
        try:
            name_filter = FieldFilter("card_name", "==", card_name.lower())
            rarity_filter = FieldFilter("rarity", "==", rarity)
            
            offers = (self.db.collection(COLLECTIONS['offers'])
                     .where(filter=name_filter)
                     .where(filter=rarity_filter)
                     .stream())
            
            result = []
            for offer in offers:
                offer_data = offer.to_dict()
                user_info = await self.get_user_info(offer_data['user_id'])
                if user_info:
                    offer_data['user_info'] = user_info
                result.append(offer_data)
                
            return result
        except Exception as e:
            logging.error(f"Error checking existing card: {str(e)}")
            raise