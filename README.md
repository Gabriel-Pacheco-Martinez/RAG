## Instructions/Instrucciones
Please use the following commands to run the code
```bash
python -m app.cli -i. # ingest code
python -m app.cli -q "query" # query code
python -m app.cli -s # server to receive queries
```

## To-Do Prototype:
1.- Create artificial chunks from document [Check]
2.- Vinculate resulting chunks with related chunks through hierarchy [Check]
3.- Prompt LLM with context [Check]
4.- Give an endpoint to ask questions [Check]
5.- Test with free API models for faster responses [Check]
6.- Refactor code for multiple LLMs [Check]
7.- Aumentar loading y chunking
8.- Test with two documents

## To-Do full project:
1.- Aumentar errores cuando no encuentra vectores (poca similitud)
2.- Add tries/catches
    - A veces los modelos no dan respuestas
3.- Ver temas de memoria, caching, latency y system design.
4.- Empezar a aumentar infra