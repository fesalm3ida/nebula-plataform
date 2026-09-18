#!/usr/bin/env bash
#
# Gera o build WEB do portal (usuário + administrador) apontando para as APIs
# públicas e copia o resultado para "deploy/web" — pasta versionada que o
# Render Static Site serve.
#
# Uso:
#   ./build_web.sh [URL_DA_API_BFF] [ADMIN_PATH]
#
# Exemplo:
#   ./build_web.sh https://nebula-admin-ciri.onrender.com painel-nbl-7f2c9a
set -euo pipefail

API_URL="${1:-https://nebula-admin-ciri.onrender.com}"
ADMIN_PATH="${2:-painel-nbl-7f2c9a}"

cd "$(dirname "$0")"

echo "==> Gerando build (API: ${API_URL} | ADMIN_PATH: ${ADMIN_PATH})"

flutter build web --release \
  --dart-define=NEBULA_ADMIN_API="${API_URL}" \
  --dart-define=ADMIN_PATH="${ADMIN_PATH}"

echo "==> Copiando para deploy/web (pasta servida pelo Render)"
rm -rf deploy/web
mkdir -p deploy
cp -r build/web deploy/web

echo
echo "OK! Agora versione a pasta e envie:"
echo "  cd ../../  &&  git add frontend/nebula-admin/deploy  &&  git commit -m \"build(portal): web\"  &&  git push"
echo
echo "Acessos:"
echo "  Usuário:       https://<portal>/"
echo "  Administrador: https://<portal>/#/${ADMIN_PATH}"
