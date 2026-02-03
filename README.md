## Instructions/Instrucciones
Please use the following commands to run the code
```bash
python -m app.cli -i. # ingest code
python -m app.cli -q "query" # query code
python -m app.cli -s # server to receive queries
```

## Important remarks
- The metadata file a json, but when converted to an object is a map with keys "documents, capitulos, subcapitulos, tabs, secciones, subsecciones, chunks".


## To-Do
- 1. Do retreival
- 2. Connect both projects
- 3. Add memory
- 4. Improve retreival (BM25+Vectors) + Re raking

## To-Do long term
- 1. Make asynchronous. Only initialize objects once
- 2. Aumentar errores cuando no encuentra vectores (poca similitud)
- 3. Add tries/catches
- 4. Infra (caching, latency, system design)
