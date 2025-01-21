<<<<<<< HEAD
# s.monti-s.cambi
=======
# Pokemon Trading Card Game Bot

Un bot Telegram per facilitare lo scambio di carte del Pokemon Trading Card Game tra collezionisti. Il bot permette agli utenti di offrire carte, cercare carte specifiche e ricevere notifiche quando viene trovata una corrispondenza.

## Caratteristiche Principali

Il bot offre diverse funzionalità per gestire gli scambi di carte Pokemon:

- Offerta di carte per lo scambio, specificando nome e rarità
- Ricerca di carte specifiche nel database
- Visualizzazione delle proprie carte offerte
- Visualizzazione delle proprie ricerche attive
- Lista completa delle carte disponibili, organizzata alfabeticamente
- Sistema di notifiche automatiche quando viene trovata una corrispondenza
- Supporto per diversi livelli di rarità delle carte

## Tecnologie Utilizzate

Il progetto è costruito utilizzando:

- Python 3.11
- python-telegram-bot per l'interfaccia con Telegram
- Google Cloud Firestore come database
- Google Cloud Platform per l'hosting e l'autenticazione

## Struttura del Progetto

```
ptcgpbot/
├── src/
│   ├── bot/
│   │   ├── __init__.py
│   │   ├── handlers.py      # Gestori dei comandi del bot
│   │   └── keyboards.py     # Layout delle tastiere inline
│   ├── database/
│   │   ├── __init__.py
│   │   └── firestore.py     # Interfaccia con il database
│   ├── utils/
│   │   ├── __init__.py
│   │   └── constants.py     # Costanti e configurazioni
│   └── main.py             # Punto di ingresso dell'applicazione
├── requirements.txt        # Dipendenze del progetto
└── README.md
```

## Configurazione

1. Creare un nuovo bot su Telegram tramite BotFather e ottenere il token
2. Configurare un progetto su Google Cloud Platform
3. Creare un file `.env` nella root del progetto con:
```
TELEGRAM_BOT_TOKEN=your_bot_token
GOOGLE_CLOUD_PROJECT=your_project_id
```
4. Configurare le credenziali di Google Cloud:
   - Scaricare il file delle credenziali del service account
   - Salvarlo come `service-account-key.json` nella directory `/app`

## Installazione

1. Clonare il repository:
```bash
git clone https://github.com/yourusername/ptcgpbot.git
cd ptcgpbot
```

2. Creare e attivare un ambiente virtuale:
```bash
python -m venv venv
source venv/bin/activate  # Per Unix/MacOS
venv\Scripts\activate     # Per Windows
```

3. Installare le dipendenze:
```bash
pip install -r requirements.txt
```

## Utilizzo

Per avviare il bot:
```bash
PYTHONPATH=$PYTHONPATH:. python3 src/main.py
```

### Comandi Disponibili

- `/start` - Avvia il bot e registra l'utente
- `/offri` - Offri una carta per lo scambio
- `/cerca` - Cerca una carta specifica
- `/lemiecarte` - Visualizza le tue carte offerte
- `/lemiericerche` - Visualizza le tue ricerche attive
- `/cartedisponibili` - Mostra tutte le carte disponibili

## Sistema di Rarità

Il bot supporta diversi livelli di rarità per le carte:
- ⬥ - Comune
- ⬥⬥ - Non Comune
- ⬥⬥⬥ - Raro
- ⬥⬥⬥⬥ - EX
- ★ - Speciale

## Architettura del Database

Il database Firestore è organizzato in tre collezioni principali:

1. `offers` - Contiene le offerte di carte
   - user_id: ID dell'utente Telegram
   - card_name: Nome della carta (lowercase)
   - rarity: Simbolo della rarità
   - timestamp: Data di inserimento

2. `searches` - Contiene le ricerche attive
   - user_id: ID dell'utente Telegram
   - card_name: Nome della carta cercata (lowercase)
   - rarity: Rarità desiderata
   - timestamp: Data di inserimento

3. `users` - Informazioni degli utenti
   - id: ID Telegram dell'utente
   - username: Username Telegram
   - first_name: Nome dell'utente
   - last_name: Cognome dell'utente
   - last_active: Ultimo accesso

## Funzionalità Future Pianificate

- Supporto per le immagini delle carte
- Sistema di feedback per gli scambi completati
- Filtri avanzati per la ricerca delle carte
- Supporto per le condizioni delle carte
- Sistema di valutazione del prezzo delle carte
- Integrazione con API esterne per informazioni sulle carte

## Contribuire

Le pull request sono benvenute. Per cambiamenti maggiori, aprite prima un issue per discutere cosa vorreste modificare.

## Licenza

[MIT](https://choosealicense.com/licenses/mit/)
>>>>>>> bed409e (init commit)
