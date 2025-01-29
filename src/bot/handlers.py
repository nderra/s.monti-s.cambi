from datetime import datetime
import logging
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes, 
    ConversationHandler, 
    CommandHandler, 
    CallbackQueryHandler
)
from database.database import Database
from utils.constants import MESSAGES, RARITY_LEVELS
from bot.keyboards import get_rarity_keyboard, get_confirmation_keyboard, get_my_items_keyboard

# Stati per la conversazione di offerta e ricerca
SET_SELECTION, RARITY_SELECTION, CARD_SELECTION = range(3)
SEARCH_SET_SELECTION, SEARCH_RARITY_SELECTION, SEARCH_CARD_SELECTION = range(3, 6)

# Ordine delle rarità
RARITY_ORDER = [
    "One Diamond",
    "Two Diamond", 
    "Three Diamond",
    "Four Diamond",
    "One Star"
]

class PokemonTradeBot:
    def __init__(self):
        self.db = Database()

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        keyboard = [
            ['/offri', '/cerca'],
            ['/lemiecarte', '/lemiericerche'],
            ['/cartedisponibili', '/matches']
        ]
        user = update.effective_user
        try:
            await self.db.save_user({
                'id': user.id,
                'username': user.username,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'is_bot': user.is_bot,
                'language_code': user.language_code,
                'last_active': datetime.now().isoformat()
            })
            await update.message.reply_text(
                MESSAGES['welcome'],
                reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
            )
        except Exception as e:
            logging.error(f"Error in start command: {str(e)}")
            await update.message.reply_text("Si è verificato un errore durante l'avvio. Riprova più tardi.")

    async def offer_card(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            sets = await self.db.get_all_sets()
            keyboard = []
            for set_data in sets:
                keyboard.append([InlineKeyboardButton(
                    set_data['set_name'],
                    callback_data=f"set_{set_data['set_code']}"
                )])
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(
                "Seleziona l'espansione:",
                reply_markup=reply_markup
            )
            return SET_SELECTION
        except Exception as e:
            logging.error(f"Error in offer_card: {str(e)}")
            await update.message.reply_text("Si è verificato un errore. Riprova più tardi.")
            return ConversationHandler.END

    async def handle_set_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        try:
            set_code = query.data.replace('set_', '')
            context.user_data['selected_set'] = set_code
            
            keyboard = []
            for rarity_name in RARITY_ORDER:
                callback_data = f"rarity|{rarity_name}"
                keyboard.append([InlineKeyboardButton(
                    RARITY_LEVELS[rarity_name]['symbol'],
                    callback_data=callback_data
                )])
            
            await query.edit_message_text(
                "Seleziona la rarità della carta:",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            return RARITY_SELECTION
        except Exception as e:
            logging.error(f"Error in handle_set_selection: {str(e)}")
            await query.edit_message_text("Si è verificato un errore. Riprova più tardi.")
            return ConversationHandler.END

    async def handle_rarity_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        try:
            _, rarity = query.data.split('|')
            set_code = context.user_data['selected_set']
            context.user_data['selected_rarity'] = rarity
            
            cards = await self.db.get_cards_by_rarity(set_code, rarity)
            keyboard = []
            for card in cards:
                keyboard.append([InlineKeyboardButton(
                    f"{card['card_name']} {RARITY_LEVELS[rarity]['symbol']}",
                    callback_data=f"card_{card['id']}"
                )])
            
            if not keyboard:
                await query.edit_message_text(
                    f"Non ci sono carte disponibili con questa rarità {RARITY_LEVELS[rarity]['symbol']}"
                )
                return ConversationHandler.END
            
            await query.edit_message_text(
                f"Seleziona la carta da offrire {RARITY_LEVELS[rarity]['symbol']}:",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            return CARD_SELECTION
        except Exception as e:
            logging.error(f"Error in handle_rarity_selection: {e}")
            await query.edit_message_text("Si è verificato un errore. Riprova più tardi.")
            return ConversationHandler.END

    async def handle_card_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        try:
            card_id = query.data.replace('card_', '')
            
            # Recupera i dettagli della carta
            card = await self.db.get_card_by_id(card_id)
            if not card:
                await query.edit_message_text("Errore nel recupero della carta. Riprova.")
                return ConversationHandler.END
            
            # Salva l'offerta
            offer_id = await self.db.save_offer(
                update.effective_user.id,
                card['card_name'],
                context.user_data['selected_rarity']
            )

            # Cerca match
            matches = await self.db.find_matching_searches(
                card['card_name'],
                context.user_data['selected_rarity']
            )
            await query.edit_message_text(MESSAGES['offer_saved'])

            # Notifica i match
            for match in matches:
                user_info = await self.db.get_user_info(update.effective_user.id)
                contact_info = f"@{user_info['username']}" if user_info.get('username') else "l'utente"
                
                await context.bot.send_message(
                    chat_id=match['user_id'],
                    text=f"📢 {contact_info} ha offerto una carta che stai cercando!\n"
                         f"Carta: {card['card_name']} ({RARITY_LEVELS[context.user_data['selected_rarity']]['symbol']})"
                )

            context.user_data.clear()
            return ConversationHandler.END
        except Exception as e:
            logging.error(f"Error in handle_card_selection: {str(e)}")
            await query.edit_message_text("Si è verificato un errore. Riprova più tardi.")
            return ConversationHandler.END

    async def search_card(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            sets = await self.db.get_all_sets()
            keyboard = []
            for set_data in sets:
                keyboard.append([InlineKeyboardButton(
                    set_data['set_name'],
                    callback_data=f"search_set_{set_data['set_code']}"
                )])
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(
                "Seleziona l'espansione da cercare:",
                reply_markup=reply_markup
            )
            return SEARCH_SET_SELECTION
        except Exception as e:
            logging.error(f"Error in search_card: {str(e)}")
            await update.message.reply_text("Si è verificato un errore. Riprova più tardi.")
            return ConversationHandler.END

    async def handle_search_set_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        try:
            set_code = query.data.replace('search_set_', '')
            context.user_data['selected_set'] = set_code
            
            keyboard = []
            for rarity_name in RARITY_ORDER:
                callback_data = f"search_rarity|{rarity_name}"
                keyboard.append([InlineKeyboardButton(
                    RARITY_LEVELS[rarity_name]['symbol'],
                    callback_data=callback_data
                )])
            
            await query.edit_message_text(
                "Seleziona la rarità della carta da cercare:",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            return SEARCH_RARITY_SELECTION
        except Exception as e:
            logging.error(f"Error in handle_search_set_selection: {str(e)}")
            await query.edit_message_text("Si è verificato un errore. Riprova più tardi.")
            return ConversationHandler.END

    async def handle_search_rarity_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        try:
            _, rarity = query.data.split('|')
            set_code = context.user_data['selected_set']
            context.user_data['selected_rarity'] = rarity
            
            cards = await self.db.get_cards_by_rarity(set_code, rarity)
            keyboard = []
            for card in cards:
                keyboard.append([InlineKeyboardButton(
                    f"{card['card_name']} {RARITY_LEVELS[rarity]['symbol']}",
                    callback_data=f"search_card_{card['id']}"
                )])
            
            if not keyboard:
                await query.edit_message_text(
                    f"Non ci sono carte disponibili con questa rarità {RARITY_LEVELS[rarity]['symbol']}"
                )
                return ConversationHandler.END
            
            await query.edit_message_text(
                f"Seleziona la carta che stai cercando {RARITY_LEVELS[rarity]['symbol']}:",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            return SEARCH_CARD_SELECTION
        except Exception as e:
            logging.error(f"Error in handle_search_rarity_selection: {e}")
            await query.edit_message_text("Si è verificato un errore. Riprova più tardi.")
            return ConversationHandler.END

    async def handle_search_card_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        try:
            card_id = query.data.replace('search_card_', '')
            
            # Recupera i dettagli della carta
            card = await self.db.get_card_by_id(card_id)
            if not card:
                await query.edit_message_text("Errore nel recupero della carta. Riprova.")
                return ConversationHandler.END
            
            # Salva la ricerca
            search_id = await self.db.save_search(
                update.effective_user.id,
                card['card_name'],
                context.user_data['selected_rarity']
            )

            # Cerca offerte esistenti
            existing_offers = await self.db.find_matching_offers(
                card['card_name'],
                context.user_data['selected_rarity']
            )

            message = MESSAGES['search_saved']
            if existing_offers:
                message += "\n\nHo trovato delle offerte esistenti:\n"
                for offer in existing_offers:
                    user_info = await self.db.get_user_info(offer['user_id'])
                    contact = f"@{user_info.get('username')}" if user_info and user_info.get('username') else "l'utente"
                    message += f"• Offerta da {contact}\n"

            await query.edit_message_text(message)
            context.user_data.clear()
            return ConversationHandler.END
        except Exception as e:
            logging.error(f"Error in handle_search_card_selection: {str(e)}")
            await query.edit_message_text("Si è verificato un errore. Riprova più tardi.")
            return ConversationHandler.END

    async def view_my_cards(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
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

    async def view_all_cards(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            cards = await self.db.get_all_cards()

            if not cards:
                await update.message.reply_text("Non ci sono carte disponibili al momento.")
                return

            message = "Tutte le carte disponibili:\n\n"
            for card in cards:
                message += f"• {card['card_name'].title()} {RARITY_LEVELS[card['rarity']]['symbol']} - {card['users']}\n"

            await update.message.reply_text(message)
        except Exception as e:
            logging.error(f"Error in view_all_cards: {str(e)}")
            await update.message.reply_text("Si è verificato un errore nel recupero delle carte.")

    async def view_matches(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            matches = await self.db.get_user_matches(update.effective_user.id)
            if not matches:
                await update.message.reply_text("Non hai match attivi.")
                return

            message = "I tuoi match:\n\n"
            for match in matches:
                message += (f"• {match['card_name'].title()} {match['rarity']}\n"
                          f"  Offerta da @{match['username']}\n"
                          f"  Clicca per completare lo scambio: /completascambio_{match['search_id']}_{match['offer_id']}\n\n")

            await update.message.reply_text(message)
        except Exception as e:
            logging.error(f"Error in view_matches: {str(e)}")
            await update.message.reply_text("Errore nel recupero dei match.")

    async def complete_trade(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            command = update.message.text.split('_')
            if len(command) != 3:
                await update.message.reply_text("Comando non valido")
                return

            search_id = int(command[1])
            offer_id = int(command[2])

            await self.db.complete_trade(search_id, offer_id)
            await update.message.reply_text("Scambio completato con successo!")
        except Exception as e:
            logging.error(f"Error in complete_trade: {str(e)}")
            await update.message.reply_text("Errore nel completamento dello scambio.")

    async def cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Annulla l'operazione corrente"""
        await update.message.reply_text('Operazione annullata.')
        context.user_data.clear()
        return ConversationHandler.END

    def get_offer_conversation(self):
        """Crea e restituisce il conversation handler per il comando /offri"""
        return ConversationHandler(
            entry_points=[CommandHandler('offri', self.offer_card)],
            states={
                SET_SELECTION: [
                    CallbackQueryHandler(self.handle_set_selection, pattern='^set_')
                ],
                RARITY_SELECTION: [
                    CallbackQueryHandler(self.handle_rarity_selection, pattern='^rarity\\|')
                ],
                CARD_SELECTION: [
                    CallbackQueryHandler(self.handle_card_selection, pattern='^card_')
                ]
            },
            fallbacks=[CommandHandler('cancel', self.cancel)]
        )

    def get_search_conversation(self):
        """Crea e restituisce il conversation handler per il comando /cerca"""
        return ConversationHandler(
            entry_points=[CommandHandler('cerca', self.search_card)],
            states={
                SEARCH_SET_SELECTION: [
                    CallbackQueryHandler(self.handle_search_set_selection, pattern='^search_set_')
                ],
                SEARCH_RARITY_SELECTION: [
                    CallbackQueryHandler(self.handle_search_rarity_selection, pattern='^search_rarity\\|')
                ],
                SEARCH_CARD_SELECTION: [
                    CallbackQueryHandler(self.handle_search_card_selection, pattern='^search_card_')
                ]
            },
            fallbacks=[CommandHandler('cancel', self.cancel)]
        )


    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            if 'searching_rarity' in context.user_data:
                rarity = context.user_data['searching_rarity']
                card_name = update.message.text

                existing_offers = await self.db.find_matching_offers(card_name, rarity)

                if existing_offers:
                    message = f"Ho trovato delle offerte esistenti per {card_name}:\n\n"
                    for offer in existing_offers:
                        user_info = await self.db.get_user_info(offer['user_id'])
                        contact = f"@{user_info.get('username')}" if user_info and user_info.get('username') else "l'utente"
                        message += f"• Offerta da {contact}\n"
                    await update.message.reply_text(message)

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
