# STEPS 

## 📘 TO-DO (POSSIBLE)
- Mostrar de donde se obtuvo la informacion en el output
- Confidence gate: Si el confidence score de los chunks es muy bajo se debe borrar el contexto actual y memoria, indicar al usuario que se esta borrando contexto actual y memoria, devolver un mensaje al usuario pidiendo un query nuevo.
- Tal vez el reranker pueda cambiar el numero de top-K chunks dependiendo de los scores.
- Avisar despues de 15 minutos si se cerró la sesión de REDIS.
- Security layer for user messages.

## 📔 REVISAR CAPITULOS
- **linea de credito**: es muy general no se entiende.

## 🧪 UNIT TESTS
Los unit tests se pueden correr con los siguientes comandos.
  - PYTHONPATH=. pytest -s  # Show prints on successful runs
  - PYTHONPATH=. pytest -vv tests/test_my_file.py # Specific file

## 💵 PRICES
Asumiendo que vamos a usar [GPT-5 nano](https://developers.openai.com/api/docs/models/gpt-5-nano). Estamos calculando utilizando el siguiente [tokenizer](https://platform.openai.com/tokenizer) para el modelo GPT-5x.

### Input
- Token count: 942 + 1693 + 1501 = 4136
- Precio: *0.05* por *4,136* dividido *1,000,000*
  - **USD:** 0.0002068 $
  - **Bs (1 USD = 10 Bs):** 0.002068 Bs 

### Output:
- Token count: 36 + 61 + 294 = 391
- Precio: *0.4* por *391* dividido *1,000,000*
  - **USD:** 0.0001564 $
  - **Bs (1 USD = 10 Bs):** 0.001564 Bs 

### Total:
**0.003632 Bs por pedido. Aproximadamente 275 pedidos seran un 1 Bs.**
