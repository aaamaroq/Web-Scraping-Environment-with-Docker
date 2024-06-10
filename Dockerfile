# Usa la imagen base de Python 3.8
FROM python:3.8

# Copia los archivos del directorio actual al contenedor de trabajo
COPY . /app

# Cambia al directorio de trabajo
WORKDIR /app

# Instala las dependencias del sistema
RUN apt-get update && \
    apt-get install -y wget unzip && \
    wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - && \
    sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list' && \
    apt-get -y update && \
    apt-get -y install google-chrome-stable

# Descarga e instala ChromeDriver
RUN wget -O /tmp/chromedriver.zip http://chromedriver.storage.googleapis.com/`curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE`/chromedriver_linux64.zip && \
    unzip /tmp/chromedriver.zip -d /usr/local/bin/

# Establece la variable de entorno para la pantalla de visualización
ENV DISPLAY=:99

# Instala las dependencias de Python
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Exponer el puerto de FastAPI
EXPOSE 8000

# Comando para ejecutar el servidor de FastAPI
CMD ["uvicorn", "scrape_azlyrics:app", "--host", "0.0.0.0", "--port", "8000"]
