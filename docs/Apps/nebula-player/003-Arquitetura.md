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

Solicita playlist

↓

Nebula Core valida o dispositivo

↓

Nebula Core entrega a playlist

↓

Player reproduz

↓

Playlist permanece apenas em memória

↓

Aplicativo é fechado

↓

Playlist descartada


--- 

Isso traz algumas vantagens:

🔒 Menor exposição de URLs e credenciais.

🔄 O backend pode trocar playlists ou servidores sem intervenção do usuário.

📡 Facilita implementar failover e balanceamento de carga.

🧠 Mantém toda a lógica de negócio centralizada no Nebula Core.

