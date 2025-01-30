import logging
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from bot.handlers import PokemonTradeBot  # Import assoluto
from utils.constants import BOT_TOKEN  # Import assoluto
from telegram import InlineKeyboardButton, InlineKeyboardMarkup


# Configurazione del logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

def main():
    """
    Funzione principale che avvia il bot
    """
    # Creiamo l'applicazione con il token del bot
    application = Application.builder().token(BOT_TOKEN).build()

    # Instanziamo il nostro bot
    pokemon_bot = PokemonTradeBot()
    application.add_handler(pokemon_bot.get_offer_conversation())
    application.add_handler(pokemon_bot.get_search_conversation())

    # Aggiungiamo gli handler per i vari comandi
    application.add_handler(CommandHandler("start", pokemon_bot.start))
    application.add_handler(CommandHandler("offri", pokemon_bot.offer_card))
    application.add_handler(CommandHandler("cerca", pokemon_bot.search_card))
    application.add_handler(CommandHandler("lemiecarte", pokemon_bot.view_my_cards))
    application.add_handler(CommandHandler("lemiericerche", pokemon_bot.view_my_searches))
    application.add_handler(CommandHandler("cartedisponibili", pokemon_bot.view_all_cards))
    application.add_handler(CommandHandler("wanted", pokemon_bot.wanted))
    application.add_handler(CommandHandler("matches", pokemon_bot.view_matches))
    application.add_handler(CommandHandler("completascambio", pokemon_bot.complete_trade))
    application.add_handler(CommandHandler("eliminaofferta", pokemon_bot.delete_offer))
    application.add_handler(CommandHandler("eliminaricerca", pokemon_bot.delete_search))

    # Handler per i messaggi di testo
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, pokemon_bot.handle_message))
    application.add_handler(CallbackQueryHandler(pokemon_bot.handle_deletion, pattern='^(del_|back_)'))

    # Avviamo il bot
    logging.info("Bot avviato!")
    application.run_polling()

if __name__ == '__main__':
    main()
