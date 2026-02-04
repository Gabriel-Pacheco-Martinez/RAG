## Instructions/Instrucciones
Please use the following commands to run the code
```bash
python -m app.cli -i. # ingest code
python -m app.cli -q "query" # query code
python -m app.cli -s # server to receive queries
```

## Important remarks
- The metadata file a json, but when converted to an object is a map with keys "documents, capitulos, subcapitulos, tabs, secciones, subsecciones, chunks".

## Todays task
- Add memory to the conversation
- Should i add like a little title to each section?

## To-Do
- 1. Do retreival [CHECK]
- 2. Connect both projects [CHECK]
- 3. Add memory
- 4. Improve retreival (BM25+Vectors) + Re raking

## To-Do long term
- 1. Make asynchronous. Only initialize objects once
- 2. Aumentar errores cuando no encuentra vectores (poca similitud)
- 3. Add tries/catches
- 4. Infra (caching, latency, system design)

## TO-DO
- Response manager:
    - Si se dio informacion para todos los slots marcar como completado.
    - Si falta un slot, mandar un mensaje pidiendo ese slot.
    - Si la confianza es muy baja. Pedir otro mensaje
- Añadir un hook que diga gracias se completo la sesion cuando se acabe el cache de REDIS.
- Debe guardar una memoria en disk con la informacion del cliente actual. Puede estar relacionado con su numero.

## Running the program
### Batch file
This method allows you to run the program with a single query for testing purposes:

```bash
./run_detect.sh
```

## REDIS
Redis is used to store session data for conversations with each user, effectively providing memory for the chatbot.

##### First time setup
To create the Redis Docker container along with the RedisInsight GUI for the first time, run:

```bash
docker run -d --name redis-stack -p 6379:6379 -p 8001:8001 redis/redis-stack:latest
```

##### Managing the container
Once the container has been created, you can use the following commands:
```bash
docker start redis-stack           # Start the container
docker stop redis-stack            # Stop the container
docker rm redis-stack              # Remove the container
docker exec -it redis-stack redis-cli  # Access Redis CLI inside the container
```

###### GUI
The GUI for the DB can be accessed in localhost:8001.

## LLM
Lo que deberia entrar al LLM es lo siguiente.

- Eres Carlitos, un asistente lógico de un sistema de pagos móviles. Tu objetivo es clasificar la intención de un mensaje y extraer entidades (monto, destinatario, concepto).

- Explicacion de QR y reglas de respuesta.

- Memoria: lo que se extrae de REDIS. 

- Slots por intencion

- Schema de respuesta
