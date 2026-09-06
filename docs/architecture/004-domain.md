---
tipo: Dominio
id: arch-004-domain
projeto: Nebula Platform
versao: 0.1.0
atualizacao: '2026-07-01'
relacionados:
- '[[arch-003-architecture]]'
- '[[arch-005-database]]'
- '[[arch-006-API]]'
- '[[arch-007-telemetry]]'
- '[[arch-008-security]]'
- '[[arch-010-glossary]]'
- '[[arch-011-principles]]'
tags:
- dominio
aliases:
- arch-004-domain
---

# Documento

**Projeto:** Nebula Platform

**Documento:** Domínio

**Versão:** 0.1.0

**Data de Atualização:** 01/07/2026

---

# Objetivo

Este documento descreve o domínio da Nebula Platform.

O objetivo é representar o negócio da plataforma antes da modelagem do banco de dados e da implementação do software.

Todas as entidades, relacionamentos e regras de negócio descritos aqui servirão como base para os demais documentos da plataforma.


# Universo Nebula 

## Pessoas 
Administrador

Cliente

## Dispositivos 
Dispositivo

## Conteúdo 
ContentProvider

ProviderAccount

Servidor

ContentEndpoint

Categoria

Canal

VOD

Série

EPG

## Operação 
Ativação

Sessão

Heartbeat

Telemetria

Logs

Eventos


## Plataforma 
Configuração

Permissão

Versão

Feature Flag

---
---

# Regras do universo 

## Regra 001 
> 1. Um dispositivo pertence a apenas um cliente. 
> 2. Um cliente pode ter mais de um dispositivo. 

## Regra 002 
> 1. Um ContentProvider pode possuir várias ProviderAccounts.
> 2. Uma ProviderAccount pertence a apenas um ContentProvider.
> 3. Uma ProviderAccount pode possuir vários Servers.
> 4. Um Server pertence a apenas uma ProviderAccount.
> 5. Um Server pode disponibilizar um ou mais ContentEndpoints.
> 6. Um ContentEndpoint pertence a apenas um Server.

## Regra 003 
> 1. Um dispositivo pode estar ativo ou bloqueado

## Regra 004 
> 1. Apenas administradores podem cadastrar e autorizar ContentEndpoints. 

## Regra 005 
> 1. O Nebula Player nunca armazena permanentemente recursos de conteúdo autorizados nem credenciais. 

