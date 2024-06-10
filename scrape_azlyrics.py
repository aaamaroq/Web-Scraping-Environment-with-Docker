import urllib.parse
from fastapi import FastAPI
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

app = FastAPI()


# Función para configurar el servicio del WebDriver
def setup_driver():
    service = Service(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(service=service, options=options)
    return driver

# Función para extraer los enlaces y títulos de las canciones
def extract_song_data(elements):
    results = {}
    for element in elements:
        try:
            link = element.find_element(By.TAG_NAME, 'a')
            title = link.find_element(By.TAG_NAME, 'b').text.replace("\\", "").replace("\"", "").replace('"', "")
            song_url = link.get_attribute('href')
            results[title] = song_url
        except Exception:
            pass
    return results


# Función para buscar canciones y devolver una lista de resultados
def search_songs(driver, key, song_name, limit=None):
    encoded_song_name = song_name.replace(" ", "%20")
    url = f'https://search.azlyrics.com/search.php?q={encoded_song_name}&x={key}'
    driver.get(url)
    elements = driver.find_elements(By.CLASS_NAME, 'visitedlyr')
    if limit:
        elements = elements[:limit]
    results = extract_song_data(elements)
    return results



# Función para obtener la letra de una canción dada su URL
def get_lyrics_for_url(driver, song_url):
    if not song_url:
        return None
    driver.get(song_url)
    try:
        lyrics_element = driver.find_element(By.XPATH, '/html/body/div[2]/div[2]/div[2]/div[5]')
        lyrics = lyrics_element.text if lyrics_element else None
        lyrics = lyrics.replace("\n", " ")
        return lyrics
    except Exception as e:
        print(f"Error obtaining lyrics: {e}")
        return None

@app.get("/songs/{key}/{song_name}")
def list_songs(song_name: str,key: str):
    print(f"Received request for key: {key} and song_name: {song_name}")
    driver = setup_driver()
    try:
        result = search_songs(driver, key, song_name)
        return result
    finally:
        driver.quit()

@app.get("/song/{key}/{song_name}")
def get_song(song_name: str,key: str):
    print(f"Received request for key: {key} and song_name: {song_name}")
    driver = setup_driver()
    try:
        result = search_songs(driver, key, song_name, limit=1)
        return result
    finally:
        driver.quit()

@app.get("/getLyrics/{key}/{song_name}")
def get_lyrics(song_name: str,key: str):
    print(f"Received request for key: {key} and song_name: {song_name}")
    driver = setup_driver()
    try:
        songs = search_songs(driver, key, song_name, limit=1)
        song_url = list(songs.values())[0]
        result = get_lyrics_for_url(driver, song_url)
        return result
    finally:
        driver.quit()
