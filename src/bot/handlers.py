from datetime import datetime
import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes
from database.database import Database
from utils.constants import MESSAGES, RARITY_LEVELS
from bot.keyboards import get_rarity_keyboard, get_confirmation_keyboard, get_my_items_keyboard

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
       keyboard = get_rarity_keyboard('offer')
       await update.message.reply_text(
           MESSAGES['select_rarity'],
           reply_markup=keyboard
       )

   async def search_card(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
       keyboard = get_rarity_keyboard('search')
       await update.message.reply_text(
           MESSAGES['select_rarity'],
           reply_markup=keyboard
       )

   async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
       query = update.callback_query
       await query.answer()

       if query.data.startswith('offer_rarity_'):
           rarity = query.data.replace('offer_rarity_', '')
           context.user_data['offering_rarity'] = rarity
           await query.edit_message_text(
               f"Hai selezionato rarità: {RARITY_LEVELS[rarity]['symbol']}\n"
               "Ora inserisci il nome della carta che vuoi offrire:"
           )
           return "WAITING_OFFER_NAME"
       
       elif query.data.startswith('search_rarity_'):
           rarity = query.data.replace('search_rarity_', '')
           context.user_data['searching_rarity'] = rarity
           await query.edit_message_text(
               f"Hai selezionato rarità: {RARITY_LEVELS[rarity]['symbol']}\n"
               "Ora inserisci il nome della carta che stai cercando:"
           )
           return "WAITING_SEARCH_NAME"

       elif query.data.startswith('complete_trade_'):
           _, search_id, offer_id = query.data.split('_')
           await self.complete_trade(search_id, offer_id)
           await query.edit_message_text("Scambio completato con successo!")

   async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
       try:
           if 'offering_rarity' in context.user_data:
               rarity = context.user_data['offering_rarity']
               card_name = update.message.text

               offer_id = await self.db.save_offer(
                   update.effective_user.id,
                   card_name,
                   rarity
               )

               matches = await self.db.find_matching_searches(card_name, rarity)
               await update.message.reply_text(MESSAGES['offer_saved'])

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
               message += f"• {card['card_name'].title()} {card['rarity']} - {card['users']}\n"
           
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
