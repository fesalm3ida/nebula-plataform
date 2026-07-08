# Convenções de Armazenamento Local

## Objetivo

Este documento define as regras de armazenamento local do Nebula Player.

O Nebula Player não utiliza PostgreSQL diretamente.

Toda persistência transacional pertence ao Nebula Core, conforme ADR-013.

---

## Tecnologias Permitidas

Para o MVP, o Nebula Player poderá utilizar:

- DataStore
- SharedPreferences
- Room/SQLite apenas se necessário

---

## Dados Permitidos

O Player poderá armazenar localmente:

- DeviceKey
- NDF
- token de sessão/autenticação
- preferências visuais
- cache temporário não sensível

---

## Dados Proibidos

O Player nunca deverá armazenar permanentemente:

- ContentEndpoints
- URLs completas sensíveis
- credenciais de provedores
- listas M3U
- regras de negócio
- dados administrativos

---

## Princípio

O Nebula Player é um cliente leve.

Ele identifica o Device, autentica-se no Nebula Core, recebe autorizações temporárias e envia telemetria.

A inteligência da plataforma permanece no Nebula Core.