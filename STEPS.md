**READ REDIS MEMORY**: Leer la memoria de REDIS y asignarla al state de LangGraph.

**TOPIC CLASSIFICATION**: La pregunta tiene relevancia a banca? A que topic va alineada la pregunta? O es la pregunta muy ambigua? 
- Necesitara un pequeño esquema de los topics
- Necesitara la ventana de contexto actual del RAG
- Necesitara los ultimos 6 mensajes
- Si la pregunta es muy ambigua volver al usuario, si no lo es rewrite query so that I can do RAG.

  * RAG_CONTEXT

**DECIDE RAG**: Con el query que esta re escrito, analizar si se deberia utilizar el RAG system una vez mas o si se puede responder con lo que existe en el context hasta el momento
  - Ahora se hara con un LLM. Se puede cambiar en el futuro por un embedding comparison.

**RETRIEVE and RERANK**: Hacer el retrieve de los top 5 chunks con Hybrid search (Dense vectors + BM25). Perform cross encoder re rank on the resulting top 5 chunks.

**CONFIDENCE GATE**: Si el confidence score de nuestros chunks es muy bajo. Se debe devolver un mensaje al usuario pidiendo un query nuevo mas detallado. "Borrar contexto actual y memoria".
  - Borrar el contexto actual y memoria
  - Indicar al usuario que se esta borrando el contexto actual y la memoria.

**BUILD PROMPT**: Utilizar el context retrieved borrando el anterior si se utilizo rag, o utilizar el context ya existente si no se utilizo rag y armar el prompt.

**PROMPT LLM**: Prompt LLM con el contexto y los ultimos mensajes.

**UPDATE REDIS MEMORY**: Updatear el memory de REDIS utilizando lo obtenido en LangGraph hasta el momento.




    # graph.add_node("clasificacion_temas", temas_clasificacion)



    # graph.add_node("load_state", load_state_from_redis)

    # graph.add_node("topic_classification", topic_classification)

    # graph.add_node("rewrite_query", rewrite_query)

    # graph.add_node("decide_rag", decide_rag_vs_memory)

    # graph.add_node("retrieve", retrieve_documents)
    # graph.add_node("rerank", cross_encoder_rerank)

    # graph.add_node("confidence_gate", pre_answer_confidence_gate)

    # graph.add_node("build_prompt", build_prompt)
    # graph.add_node("answer", llm_answer)

    # graph.add_node("save_state", save_state_to_redis)
