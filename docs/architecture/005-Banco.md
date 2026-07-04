# Documento

**Projeto:** Nebula Platform

**Módulo:** Nebula Plataforma

**Versão:** 0.1.0

**Status:** Em desenvolvimento

**Última atualização:** 02/07/2026

**Responsável:** Felipe Almeida

---

# Entidade: Device

## Definição

Um Device representa um dispositivo físico autorizado a utilizar a Nebula Platform.

Todo acesso à plataforma ocorre através de um Device.

O Device é a principal entidade operacional do sistema, sendo responsável por identificar de forma única uma instalação do Nebula Player e servir como ponto central para ativação, distribuição de recursos de conteúdo autorizados, monitoramento e telemetria.

---

# Responsabilidades

- Identificar unicamente uma instalação.
- Receber autorização do Nebula Core.
- Solicitar recursos de conteúdo autorizados.
- Reproduzir conteúdo.
- Enviar eventos de telemetria.
- Manter heartbeat periódico.

---

# Identificadores

Cada Device possui:

- UUID
- Device Key
- MAC Address (quando disponível)

A Device Key é gerada apenas uma vez durante a primeira instalação do Nebula Player.

---

# Estados

## Pending

Dispositivo registrado, porém ainda não ativado.

---

## Active

Dispositivo autorizado.

Pode consumir recursos de conteúdo autorizados e enviar telemetria.

---

## Blocked

Dispositivo bloqueado manualmente pelo administrador.

Não pode reproduzir conteúdo.

---

## Revoked

Dispositivo cuja autorização foi revogada.

Necessita nova ativação.

---

## Expired

Dispositivo cuja licença expirou.

Necessita renovação.

---

## Relacionamentos

Um Device:

- pertence a um Cliente;
- pode acessar ContentEndpoints autorizados pelo Nebula Core;
- comunica-se com o Nebula Core;
- gera eventos de Telemetria;
- gera Heartbeats;
- gera Logs.

---

## Regras

Um Device nunca poderá:

- autenticar sem uma Device Key válida;
- alterar seu próprio estado;
- cadastrar ou remover ContentEndpoints;
- alterar configurações críticas da plataforma;
- acessar recursos de conteúdo para os quais não foi autorizado;
- contornar as validações do Nebula Core.

---

# Ciclo de Vida

Instalação

↓

Device Key gerada

↓

Pending

↓

Ativação

↓

Active

↓

Reprodução

↓

Heartbeat

↓

Telemetria

↓

Blocked / Revoked / Expired
