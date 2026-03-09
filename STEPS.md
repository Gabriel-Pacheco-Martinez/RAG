# STEPS 

## 📘 TO-DO (POSSIBLE)
- Follow up question testing ✅
- Question testings
- Open AI integration
- Aclarar que la moneda nacional es en Bolivianos ✅

- Session timeout 15 minutos?
- User messages security layer?

## Artillery
npx artillery run artillery/load-test.yaml

## MODELOS RECOMENDADOS
- [LLama 3](https://ollama.com/library/llama3),[Mistral](https://mistral.ai/pricing#api), [Gemma 2](https://aistudio.google.com/app/rate-limit?project=gen-lang-client-0500425753) recommended.

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
