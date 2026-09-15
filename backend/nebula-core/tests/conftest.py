import os

# Os testes de integracao PostgreSQL APAGAM as tabelas. Para nao destruir os
# dados de desenvolvimento, eles rodam em um banco separado (`nebula_test`).
#
# Variaveis de ambiente tem precedencia sobre o `.env`, entao definir
# POSTGRES_DB aqui redireciona toda a suite.
os.environ["POSTGRES_DB"] = "nebula_test"

from app.core.config import get_settings  # noqa: E402


# Garante que o redirecionamento valha mesmo se as settings ja foram lidas.
get_settings.cache_clear()
