## Steps
- 1. **Confidence gate**: Si el confidence score de los chunks es muy bajo se debe:
  - Borrar el contexto actual y memoria
  - Indicar al usuario que se esta borrando contexto actual y memoria
  - Devolver un mensaje al usuario pidiendo un query nuevo

- 2. **Unit tests**: Crear unit tests que revise si se está retrieving la parte correcta del contexto.

- 3. **REDIS**: Avisar después de 15 minutos que se cerró la sesión de REDIS.

- 4. **Price costing**: Ver cuanto va a costar cada llamada.

- 5. **Security layer**: Security filtering layer for user messages.