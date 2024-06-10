## Introduction
Recently, I've learned about Docker technologies and wanted to put that knowledge to the test. A friend of mine needed a solution where given the title of a song, its lyrics could be obtained. So, I began this project.
In this article, I'll guide you through the creation and configuration of a web scraping environment using Docker. We'll use technologies like `FastAPI`, `Selenium`, and `Docker Compose` to set up a web application that performs scraping tasks on the AZLyrics site. The integration of these tools will enable the development of a portable and easy-to-deploy solution for web task automation.

## Service Execution and Testing

### Service Execution

To execute the service, use the following commands in the terminal:

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

We have configured and executed a web scraping service using Docker, Selenium, and FastAPI. This service allows searching for and obtaining song lyrics from the AZLyrics website in an automated manner. The Docker integration ensures that the environment is portable and easy to deploy, simplifying the development and production deployment of web scraping applications.
The anti-scraping measure of AZLyrics doesn't seem very effective, and I would recommend looking for a better alternative.