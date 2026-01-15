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
3.- Prompt LLM with context
4.- Give an endpoint to ask questions
5.- Change to smaller model on verifier llm
6.- Aumentar loading y chunking

## To-Do full project:
6.- Ver temas de memoria, caching, latency y system design.
7.- Add tries/catches
8.- Empezar a aumentar infra