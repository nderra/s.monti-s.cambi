# Usiamo un'immagine Python ufficiale slim per ridurre la dimensione
FROM python:3.11-slim

# Impostiamo le variabili d'ambiente per Python
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
ENV PORT=8080

# Creiamo e impostiamo la directory di lavoro
WORKDIR /app

# Copiamo e installiamo le dipendenze
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiamo il codice dell'applicazione
COPY src/ ./src/

# Esponiamo la porta per il server web
EXPOSE 8080

# Comando di avvio dell'applicazione
CMD ["python", "src/main.py"]