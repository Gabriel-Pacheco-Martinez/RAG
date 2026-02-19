## Steps
- **Confidence gate**: Si el confidence score de los chunks es muy bajo se debe:
  - Borrar el contexto actual y memoria
  - Indicar al usuario que se esta borrando contexto actual y memoria
  - Devolver un mensaje al usuario pidiendo un query nuevo

- **Unit tests**: Crear unit tests que revise si se está retrieving la parte correcta del contexto.

  - PYTHONPATH=. pytest -s

- **RETRIEVAL**: Tal vez necesito agarrar todo el capitulo, subcapitulo. Pero va a ser mas caro, porque se necesitaran mas tokens. Tal vez le puedo avisar al usuario que la informacion salio de tal capitulo de la pagina web para que se guien. Tal vez le puedo poner un resumen a cada pedaso de texto tambien.

- **REDIS**: Avisar después de 15 minutos que se cerró la sesión de REDIS.

- **Price costing**: Ver cuanto va a costar cada llamada. [Check]

- **Security layer**: Security filtering layer for user messages.


## Prices
Asumiendo que vamos a usar [GPT-5 nano](https://developers.openai.com/api/docs/models/gpt-5-nano). Estamos calculando utilizando el siguiente [tokenizer](https://platform.openai.com/tokenizer) para la GPT-5x.


## 🔢 Conteo de tokens
### Intent section:
- Intent input tokens: 1122
- Intent output tokens: 53

#### Classify section:
- Classify input tokens: 2080
- Classify output tokens: 221

### Generate section
- Generate input tokens: 971
- Generate output tokens: 83


## 💰 Cost Calculations
### Input Cost
*0.5* por *4,173* dividido *1,000,000*

- **USD:** 0.00020865 $
- **Bs (1 USD = 10 Bs):** 0.0020865  

### Output Cost
*0.4* por *357* dividido *1,000,000*

- **USD:** 0.0001428 $
- **Bs (1 USD = 10 Bs):** 0.001428 Bs


## 💵 Total
**0.0035145 Bs. Aproximadamente 285 requests serán igual a 1Bs.**
