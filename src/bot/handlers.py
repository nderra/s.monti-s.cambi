import logging
from telegram import Update
from telegram.ext import ContextTypes
from src.database.firestore import Database
from src.utils.constants import MESSAGES, RARITY_LEVELS
from src.bot.keyboards import get_rarity_keyboard, get_confirmation_keyboard, get_my_items_keyboard
from google.cloud import firestore

class PokemonTradeBot:
    def __init__(self):
        """Inizializza il bot con una connessione al database"""
        self.db = Database()

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Gestisce il comando /start salvando le informazioni complete dell'utente.
        """
        user = update.effective_user
        try:
            # Salviamo tutte le informazioni disponibili dell'utente
            await self.db.save_user({
                'id': user.id,
                'username': user.username,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'is_bot': user.is_bot,
                'language_code': user.language_code,
                'last_active': firestore.SERVER_TIMESTAMP
            })
            await update.message.reply_text(MESSAGES['welcome'])
        except Exception as e:
            logging.error(f"Error in start command: {str(e)}")
            await update.message.reply_text("Si è verificato un errore durante l'avvio. Riprova più tardi.")


    async def offer_card(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Gestisce il comando /offri
        Avvia il processo di offerta di una carta mostrando la tastiera delle rarità
        """
        keyboard = get_rarity_keyboard('offer')
        await update.message.reply_text(
            MESSAGES['select_rarity'],
            reply_markup=keyboard
        )

    async def search_card(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Gestisce il comando /cerca
        Avvia il processo di ricerca di una carta mostrando la tastiera delle rarità
        """
        keyboard = get_rarity_keyboard('search')
        await update.message.reply_text(
            MESSAGES['select_rarity'],
            reply_markup=keyboard
        )

    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Gestisce le callback dai bottoni inline
        """
        query = update.callback_query
        await query.answer()  # Rispondiamo subito alla callback
        
        # Gestiamo la selezione della rarità per un'offerta
        if query.data.startswith('offer_rarity_'):
            rarity = query.data.replace('offer_rarity_', '')
            context.user_data['offering_rarity'] = rarity
            await query.edit_message_text(
                f"Hai selezionato rarità: {RARITY_LEVELS[rarity]['symbol']}\n"
                "Ora inserisci il nome della carta che vuoi offrire:"
            )
            return "WAITING_OFFER_NAME"
        
        # Gestiamo la selezione della rarità per una ricerca
        elif query.data.startswith('search_rarity_'):
            rarity = query.data.replace('search_rarity_', '')
            context.user_data['searching_rarity'] = rarity
            await query.edit_message_text(
                f"Hai selezionato rarità: {RARITY_LEVELS[rarity]['symbol']}\n"
                "Ora inserisci il nome della carta che stai cercando:"
            )
            return "WAITING_SEARCH_NAME"

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Gestisce i messaggi di testo dell'utente
        """
        # Se stiamo aspettando il nome di una carta da offrire
        if 'offering_rarity' in context.user_data:
            rarity = context.user_data['offering_rarity']
            card_name = update.message.text
            
            # Salviamo l'offerta nel database
            offer_id = await self.db.save_offer(
                update.effective_user.id,
                card_name,
                rarity
            )
            
            # Cerchiamo possibili corrispondenze
            matches = await self.db.find_matching_searches(card_name, rarity)
            
            # Informiamo l'utente che l'offerta è stata salvata
            await update.message.reply_text(MESSAGES['offer_saved'])
            
            # Se ci sono corrispondenze, notifichiamo gli utenti interessati
            for match in matches:
                await context.bot.send_message(
                    chat_id=match['user_id'],
                    text=f"📢 Qualcuno ha offerto una carta che stai cercando!\n"
                         f"Carta: {card_name} ({RARITY_LEVELS[rarity]['symbol']})"
                )
            
            del context.user_data['offering_rarity']
        
        # Se stiamo aspettando il nome di una carta da cercare
        elif 'searching_rarity' in context.user_data:
            rarity = context.user_data['searching_rarity']
            card_name = update.message.text
            
            # Salviamo la ricerca nel database
            search_id = await self.db.save_search(
                update.effective_user.id,
                card_name,
                rarity
            )
            
            # Cerchiamo possibili corrispondenze
            matches = await self.db.find_matching_offers(card_name, rarity)
            
            # Informiamo l'utente che la ricerca è stata salvata
            await update.message.reply_text(MESSAGES['search_saved'])
            
            # Se ci sono corrispondenze, le mostriamo all'utente
            if matches:
                for match in matches:
                    await update.message.reply_text(
                        f"💡 Ho trovato un'offerta per questa carta!\n"
                        f"Carta: {match['card_name']} ({RARITY_LEVELS[rarity]['symbol']})"
                    )
            
            del context.user_data['searching_rarity']

    async def view_my_cards(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Gestisce il comando /lemiecarte mostrando le carte offerte dall'utente."""
        try:
            offers = await self.db.get_user_offers(update.effective_user.id)

            if not offers:
                await update.message.reply_text("Non hai ancora offerto nessuna carta.")
                return

            message = "Le tue carte offerte:\n\n"
            for offer in offers:
                message += f"• {offer['card_name'].title()} {RARITY_LEVELS[offer['rarity']]['symbol']}\n"

            await update.message.reply_text(message)
        except Exception as e:
            logging.error(f"Error in view_my_cards: {str(e)}")
            await update.message.reply_text("Si è verificato un errore. Riprova più tardi.")

    async def view_my_searches(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Gestisce il comando /lemiericerche mostrando le ricerche attive dell'utente."""
        try:
            searches = await self.db.get_user_searches(update.effective_user.id)

            if not searches:
                await update.message.reply_text("Non hai ancora nessuna ricerca attiva.")
                return

            message = "Le tue ricerche attive:\n\n"
            for search in searches:
                message += f"• {search['card_name'].title()} {RARITY_LEVELS[search['rarity']]['symbol']}\n"

            await update.message.reply_text(message)
        except Exception as e:
            logging.error(f"Error in view_my_searches: {str(e)}")
            await update.message.reply_text("Si è verificato un errore. Riprova più tardi.")

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Gestisce i messaggi di testo dell'utente, incluse le offerte e le ricerche di carte."""
        try:
            if 'offering_rarity' in context.user_data:
                rarity = context.user_data['offering_rarity']
                card_name = update.message.text

                # Salviamo l'offerta
                offer_id = await self.db.save_offer(
                    update.effective_user.id,
                    card_name,
                    rarity
                )

                # Cerchiamo corrispondenze nelle ricerche
                matches = await self.db.find_matching_searches(card_name, rarity)

                await update.message.reply_text(MESSAGES['offer_saved'])

                # Notifichiamo gli utenti interessati
                for match in matches:
                    user_info = await self.db.get_user_info(update.effective_user.id)
                    contact_info = f"@{user_info['username']}" if user_info.get('username') else "l'utente"

                    await context.bot.send_message(
                        chat_id=match['user_id'],
                        text=f"📢 {contact_info} ha offerto una carta che stai cercando!\n"
                             f"Carta: {card_name} ({RARITY_LEVELS[rarity]['symbol']})"
                    )

                del context.user_data['offering_rarity']

            elif 'searching_rarity' in context.user_data:
                rarity = context.user_data['searching_rarity']
                card_name = update.message.text

                # Controlliamo se la carta esiste già
                existing_offers = await self.db.check_existing_card(card_name, rarity)

                if existing_offers:
                    message = f"Ho trovato delle offerte esistenti per {card_name}:\n\n"
                    for offer in existing_offers:
                        user_info = offer.get('user_info', {})
                        contact = f"@{user_info.get('username', 'Unknown')}"
                        message += f"• Offerta da {contact}\n"
                    await update.message.reply_text(message)

                # Salviamo comunque la ricerca
                search_id = await self.db.save_search(
                    update.effective_user.id,
                    card_name,
                    rarity
                )

                await update.message.reply_text(MESSAGES['search_saved'])

                del context.user_data['searching_rarity']

        except Exception as e:
            logging.error(f"Error in handle_message: {str(e)}")
            await update.message.reply_text("Si è verificato un errore. Riprova più tardi.")
            
    async def view_all_cards(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Mostra tutte le carte disponibili, ordinate alfabeticamente e aggregate per carta.
        Le carte identiche offerte da utenti diversi vengono mostrate sulla stessa riga.
        """
        try:
            cards = await self.db.get_all_cards()
            
            if not cards:
                await update.message.reply_text("Non ci sono carte disponibili al momento.")
                return
            
            message = "Tutte le carte disponibili:\n\n"
            
            for card in cards:
                # Formattiamo gli utenti come una lista separata da virgole
                users_display = ", ".join(card['users'])
                
                # Aggiungiamo la carta alla lista con tutti gli utenti che la offrono
                message += f"• {card['card_name'].title()} {card['rarity']} - {users_display}\n"
            
            await update.message.reply_text(message)
        except Exception as e:
            logging.error(f"Error in view_all_cards: {str(e)}")
            await update.message.reply_text("Si è verificato un errore nel recupero delle carte.")