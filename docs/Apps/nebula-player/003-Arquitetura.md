# Documento

**Projeto:** Nebula Platform

**Módulo:** Nebula Plataforma

**Versão:** 0.1.0

**Status:** Em desenvolvimento

**Última atualização:** 01/07/2026

**Responsável:** Felipe Almeida


---


Nebula Player

↓

Solicita recursos de conteúdo autorizados

↓

Nebula Core valida o dispositivo

↓

Nebula Core entrega os recursos de conteúdo autorizados

↓

Player reproduz

↓

Recurso de conteúdo autorizado permanece apenas em memória

↓

Aplicativo é fechado

↓

Recurso de conteúdo autorizado descartado


--- 

Isso traz algumas vantagens:

🔒 Menor exposição de URLs e credenciais.

🔄 O backend pode atualizar autorizações de recursos de conteúdo sem intervenção do usuário.

📡 Facilita implementar failover e balanceamento de carga.

🧠 Mantém toda a lógica de negócio centralizada no Nebula Core.

