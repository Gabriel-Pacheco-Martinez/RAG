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
Este proyecto implementa la funcionalidad conversacional del **Chatbot Carlitos BNB** para el **Banco Nacional de Bolivia**.

El sistema permite a los usuarios interactuar con el chatbot y realizar preguntas sobre productos, servicios e información del banco en formato **Q&A**, con el objetivo de reducir tiempos de atención y mejorar la experiencia del usuario.

La arquitectura utiliza un sistema **RAG (Retrieval-Augmented Generation)** agéntico basado en **LangGraph**, junto con **Qdrant** para búsqueda vectorial y **Redis** para manejo de memoria conversacional.

## Requirements
Para ejecutar el proyecto es necesario tener instalado:

- **Docker**
- **Docker Compose**

El proyecto fue desarrollado y probado con las siguientes versiones:

- Docker `27.5.1`
- Python `3.11.10`
- Qdrant `1.16.3`
- Redis `7.4.7`

## Instructions
Para construir y ejecutar el proyecto, correr el siguiente comando en el directorio raíz:
```bash
docker compose up --build -d
```

PyTorch no debe incluirse en `requirements.txt` debido a la necesidad de gestionar versiones específicas según la arquitectura (CPU vs GPU) y los controladores de CUDA. Por ello, la instalación se realiza directamente en el `Dockerfile` de cada servidor.

Para entornos CPU, se puede instalar la versión estándar de PyTorch. Si se desea utilizar GPU con soporte CUDA, se debe especificar la versión compatible de CUDA en la línea de instalación del `Dockerfile`. Por ejemplo:
```bash
RUN pip install torch==2.5.1+cu121 --index-url https://download.pytorch.org/whl/cu121
```

Para poder construir y ejecutar el proyecto con un depurador, ya sea para corregir errores o para desarrollo, se debe utilizar el siguiente comando para habilitar el modo debug:

```bash
docker compose -f docker-compose.yml -f docker-compose.debug.yml up --build
```


## API Endpoints
**1.Construcción de la base vectorial**
Construye o actualiza la base de conocimiento vectorial en Qdrant.
```bash
GET http://127.0.0.1:8000/index
```

**2.Concersación con el chatbot**
Permite enviar mensajes al chatbot y recibir una respuesta generada por el sistema RAG.
```bash
POST http://127.0.0.1:8000/conversation
```

Esquema necesario:
```bash
{
    session_id: int   # Identificador de la sesión conversacional.
    mensaje: str      # Pregunta o mensaje enviado por el usuario.
}
```

**3.Health points para las dos APIs**
Permite revisar si los dos endpoints desarrollados "api_server" y "rag_server" estan sanos y levantados.

```bash
GET http://127.0.0.1:8000/health   # api_server
```

```bash
GET http://127.0.0.1:8080/health   # rag_server
```

