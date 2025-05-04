FROM python:3.12.2-slim

# Étape 5 : Positionnement du répertoire de travail dans le conteneur

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Étape 4 : Copie des fichiers sur windows dans le conteneur
COPY . .

# RUN test -f manage.py || django-admin startproject app .

EXPOSE 80

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]
