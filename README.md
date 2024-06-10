# Creating and Configuring a Web Scraping Environment with Docker

## Introduction
I recently learned about Docker technologies and wanted to put that knowledge to the test. A friend of mine needed a solution where given the title of a song, its lyrics could be obtained. So, I started this project.
In this article, I'll guide you through the creation and configuration of a web scraping environment using Docker. We'll use technologies like `FastAPI`, `Selenium`, and `Docker Compose` to set up a web application that performs scraping tasks on the AZLyrics site. Integrating these tools will allow us to develop a portable and easy-to-deploy solution for web automation tasks.

## Setting up the Environment with Docker

### Requirements

Before getting started, we'll need the following libraries in our `requirements.txt` file:
```
Python
Selenium
Webdriver-manager
FastAPI
Uvicorn
```

### Docker Environment Preparation
I'll set up a `Dockerfile` to create a Docker image containing a web application built with `FastAPI`. This application will also depend on a web environment (Google Chrome and ChromeDriver) where web scraping tasks will be performed. I'll explain its configuration step by step.

#### 1. Specify the base image

```dockerfile
FROM python:3.8
```

Here, I use the official `Python 3.8` image as the base. This image already contains an installation of `Python 3.8` and common tools necessary to run Python applications.

#### 2. Copy project files to the container

```dockerfile
COPY . /app
```

In the project folder, I have the `requirements.txt` file with necessary Python libraries and the `scrape_azlyrics.py` file with the scraping script. With this command, all files from the current directory on the host machine are copied to the `/app` directory inside the Docker container. This facilitates the use of these files later thanks to Docker's cache.

#### 3. Set the working directory

```dockerfile
WORKDIR /app
```
Changes the current working directory to `/app`. This simplifies subsequent instructions, as commands will be executed from the `/app` directory where the application code is located.

#### 4. Install system and web environment dependencies

```dockerfile
RUN apt-get update && \
    apt-get install -y wget unzip && \
    wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - && \
    sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list' && \
    apt-get -y update && \
    apt-get -y install google-chrome-stable
```

These commands update the `apt-get` package index, install `wget` and `unzip`, add the Google signing key for Chrome and its repository, and then install Google Chrome. `wget` and `unzip` are needed to download and unzip ChromeDriver. And Google Chrome is essential for scraping tasks that require a browser.

#### 5. Download and install ChromeDriver

```dockerfile
RUN wget -O /tmp/chromedriver.zip http://chromedriver.storage.googleapis.com/`curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE`/chromedriver_linux64.zip && \
    unzip /tmp/chromedriver.zip -d /usr/local/bin/
```

These commands download the latest version of `ChromeDriver` and unzip it into the `/usr/local/bin/` directory. `ChromeDriver` is necessary to control the Chrome browser programmatically in scraping tasks.

#### 6. Set the environment variable for the display

```dockerfile
ENV DISPLAY=:99
```

This sets the `DISPLAY` environment variable to use virtual display number 99. This configuration is useful when using a virtual X server (Xvfb) to run Chrome in headless mode.

#### 7. Install Python dependencies

```dockerfile
RUN pip install --upgrade pip && \
    pip install -r requirements.txt
```

Updates `pip` to the latest version and installs the Python dependencies listed in the `requirements.txt` file. Keeping `pip` updated ensures that you have the latest features and security fixes. The dependencies from `requirements.txt` are necessary for the application to function correctly.

#### 8. Expose the port for the FastAPI application

```dockerfile
EXPOSE 8000
```

* This is the port on which the `FastAPI` application will serve HTTP requests. Specifying it allows mapping this port to the host or other services.

#### 9. Command to start the FastAPI application

```dockerfile
CMD ["uvicorn", "scrape_azlyrics:app", "--host", "0.0.0.0", "--port", "8000"]
```

Runs `uvicorn`, the ASGI server, with the `scrape_azlyrics` module and the `app`, configuring it to listen on all network interfaces (`0.0.0.0`) and port 8000. This command starts the FastAPI application, making it accessible on the network through the specified port.

## Configuring the web scraper service
Next, I'll define the web scraper code. This code defines an API using `FastAPI` that will search for songs and fetch song lyrics from the AZLyrics website using `Selenium`. In the following code, we'll see that a *key* is required, which is an anti-scraper measure from the website, but we'll see later how it's easily bypassed.

### Code Explanation and Justification

The code defines a web application using FastAPI to search for and extract song lyrics from the AZLyrics website using Selenium WebDriver for browser automation. Here's the detailed explanation and justification of each section of the code:

#### 1. Necessary Imports

```python
import urllib.parse
from fastapi import FastAPI
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
```

These lines import the necessary modules:
- `urllib.parse` for manipulating URLs.
- `FastAPI` to create the web application.
- `selenium` and `webdriver_manager` for web navigation automation with ChromeDriver.

#### 2. FastAPI Application Creation

```python
app = FastAPI()
```

Creates an instance of the FastAPI application.

#### 3. Function to set up the WebDriver service

```python
def setup_driver():
    service = Service(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(service=service, options=options)
    return driver
```

Sets up and returns an instance of Chrome WebDriver in headless mode. Using headless mode allows running Chrome without a graphical interface, which is useful for server environments. Additional options (`--no-sandbox`, `--disable-dev-shm-usage`)...

#### 4. Function to extract song data

```python
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
```

Extracts song titles and URLs from the provided HTML elements. This allows retrieving and cleaning relevant song data from the search results page.

#### 5. Function to search for songs and return results

```python
def search_songs(driver, key, song_name, limit=None):
    encoded_song_name = song_name.replace(" ", "%20")
    url = f'https://search.azlyrics.com/search.php?q={encoded_song_name}&x={key}'
    driver.get(url)
    elements = driver.find_elements(By.CLASS_NAME, 'visitedlyr')
    if limit:
        elements = elements[:limit]
    results = extract_song_data(elements)
    return results
```

Performs a search on AZLyrics and returns a list of found songs. Automates the process of searching for songs on AZLyrics, making it easy to obtain structured data from search results.

#### 6. Function to get lyrics for a song

```python
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
```

Navigates to the URL of a specific song and extracts the lyrics. Allows fetching the content of song lyrics from an individual AZLyrics page, handling potential errors during the process.

#### 7. API Routes

```python
@app.get("/songs/{key}/{song_name}")
def list_songs(song_name: str, key: str):
    driver = setup_driver()
    try:
        result = search_songs(driver, key, song_name)
        return result
    finally:
        driver.quit()
```

Defines a route to search for songs by name and key. Allows users to search for songs and get a list of results from the API.

```python
@app.get("/song/{key}/{song_name}")
def get_song(song_name: str, key: str):
    driver = setup_driver()
    try:
        result = search_songs(driver, key, song_name, limit=1)
        return result
    finally:
        driver.quit()
```

Defines a route to search for a single song by name and key. Provides a way to quickly get the first result from a song search.

```python
@app.get("/getLyrics/{key}/{song_name}")
def get_lyrics(song_name: str, key: str):
    driver = setup_driver()
    try:
        songs = search_songs(driver, key, song_name, limit=1)
        song_url = list(songs.values())[0]
        result = get_lyrics_for_url(driver, song_url)
        return result
    finally:
        driver.quit()
```

Defines a route to get the lyrics of a specific song by name and key. Allows users to directly get the lyrics of a specific song, combining the search and lyrics extraction into a single operation.

## Configuring Docker Compose

The `docker-compose.yml` file is configured to define and run a Docker service that builds and runs the FastAPI application for scraping song lyrics. This file leverages custom image building, port mapping, volume mounts, and interactive settings to facilitate development and execution of the application.

```yaml
version: '3.8'

services:
  scrape-azlyrics:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - .:/app
    stdin_open: true
    tty: true
```

### Explanation and Justification

#### 1. Docker Compose file version

```yaml
version: '3.8'
```

Defines the version of the `docker-compose` file format to be used, in this case, version 3.8. This version is compatible with most modern Docker Compose features, providing a balance between stability and functionality.

#### 2. Service definition

```yaml
services:
  scrape-azlyrics:
```

Defines a service named `scrape-azlyrics`. A service in Docker Compose represents a container instance.

#### 3. Image building

```yaml
    build: .
```

Specifies that Docker should build the image using the Dockerfile located in the current directory (`.`). This allows Docker Compose to build the custom Docker image for the application using the instructions defined in the Dockerfile.

#### 4. Port mapping

```yaml
    ports:
      - "8000:8000"
```

Maps port 8000 of the container to port 8000 of the host. This allows the FastAPI application to be accessible from the host on port 8000.

#### 5. Volume mounts

```yaml
    volumes:
      - .:/app
```

Mounts the current directory of the host (`.`) to the `/app` directory inside the container. Mounting the working directory into the container allows any changes made to the source code files on the host to be instantly reflected in the container. This is particularly useful during development, as it allows editing the code and seeing the results without needing to rebuild the container image every time a change is made.

#### 6. Allowing open standard input (stdin)

```yaml
    stdin_open: true
```

Keeps standard input (stdin) open for the container. This option is useful for interactive applications or if access to the container via an interactive terminal is needed for debugging or testing.

#### 7. Enabling tty terminal

```yaml
    tty: true
```

Allocates a tty terminal to the container. This is useful for easier interaction with the container from the command line, providing a full terminal experience. This setting, along with `stdin_open`, allows opening an interactive session in the container, which is very useful for debugging and testing in development environments.

## Running and Testing the Service

### Running the Service

To run the service, use the following commands in the terminal:

```bash
docker-compose build
docker-compose up
```

These commands will build the Docker image and then start the container running the `FastAPI` service.

### Service Testing

To test the service, make HTTP requests to the defined routes using tools like `curl` or `Postman`, or simply through a web browser.

- To list songs: `http://localhost:8000/songs/{key}/{song_name}`
- To get song lyrics: `http://localhost:8000/song/{key}/{song_name}`

Where `{key}` is an alphanumeric key to avoid caching on AZLyrics, and `{song_name}` is the name of the song you want to search for.

## Conclusion

We have configured and run a web scraping service using Docker, Selenium, and FastAPI. This service allows searching for and obtaining song lyrics from the AZLyrics website in an automated manner. Docker integration ensures that the environment is portable and easy to deploy, simplifying the development and production deployment of web scraping applications. The anti-scraping measure by AZLyrics doesn't seem very effective, and I would recommend looking for a better alternative.

If you encounter any issues or have further questions about setting up the environment or running the service, feel free to ask!