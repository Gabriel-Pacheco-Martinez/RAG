<!-- PROJECT HEADER -->
<h1>
<p align="center">
  <img src="images/carlitosBNB.png" alt="Project Logo">
  <br> Chatbot Carlitos BNB
</p>
</h1>

<p align="center">
  Sistema RAG agentico distribuido for LangGraph para crear un Chatbot conversacional.
  <br />
  <a href="#about">About</a>
  ·
  <a href="#requirements">Requirements</a>
  ·
  <a href="#instructions">Instructions</a>
  ·
  <a href="#report">Report</a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11.10-blue?style=flat-square" alt="Python Version">
  <img src="https://img.shields.io/badge/Docker-27.5.1-lightblue?style=flat-square" alt="Docker Version">
  <img src="https://img.shields.io/badge/Qdrant-1.16.3-red?style=flat-square" alt="Qdrant Version">
  <img src="https://img.shields.io/badge/Redis-7.4.7-orange?style=flat-square" alt="Redis Version">
  <img src="https://img.shields.io/badge/License-Apache%202.0-green?style=flat-square" alt="License">
</p>


<!--  DESCRIPTION -->
## About

## Requirements


## Instructions
Please use the following shell script to initialize the server that can receive API requests at http://127.0.0.1:8000/conversation.
```bash
# Add the requirements.txt installation stuff and probably docker stuff too
./run.sh
```

The schema of the request sent in the HTTP request has to follow:
```bash
{
    session_id: int
    mensaje: str
}
```

### Redis and Qdrant
The project requires the use of REDIS and Qdrant in order to work. REDIS holds the memory of the session, while Qdrant works as the vector DB for the project. Both require DOCKER to work.

- Installation of Qdrant through Docker. A GUI can be accessed at localhost:6333
```bash
docker run -p 6333:6333 -p 6334:6334 qdrant/qdrant
```

- Installation of REDIS through Docker. A GUI can be accessed at localhost:8001
```bash
docker run -d --name redis-stack -p 6379:6379 -p 8001:8001 redis/redis-stack:latest
```
