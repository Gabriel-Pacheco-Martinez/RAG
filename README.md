## Instructions/Instrucciones
Please use the following commands to run the code
```bash
python -m app.cli -i. # ingest code
python -m app.cli -q "query" # query code
python -m app.cli -s # server to receive queries
```

## To-Do full project:
- 1.- Aumentar errores cuando no encuentra vectores (poca similitud)
- 2.- Add tries/catches
    - A veces los modelos no dan respuestas
- 3.- Ver temas de memoria, caching, latency y system design.
- 4.- Empezar a aumentar infra

## To-Do
- Confidence score to see if retry with LLM rewritten query
- Hybrid search (BM25 + Vectors)
- Re-ranking. HOW??
- Finetuning. How do we select our parameters?
- Maybe separate databases by area for better document retreival:
        - Could have sections like: chatbot, human resources, finance, credits, marketing.