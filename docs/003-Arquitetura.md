# Documento

**Projeto:** Nebula Platform

**Módulo:** Nebula Plataforma

**Versão:** 0.1.0

**Status:** Em desenvolvimento

**Última atualização:** 01/07/2026

**Responsável:** Felipe Almeida

---
---


# 1. O Player é "stateless" sempre que possível

Em vez de armazenar playlists e configurações localmente, ele consulta o Core quando necessário e mantém apenas o mínimo indispensável para funcionar. Isso simplifica atualizações e reduz o risco de inconsistências.

# 2. O Nebula Core não conhece detalhes do player

O Core responde a APIs e aplica regras de negócio, mas não depende da interface Android. Assim, no futuro, um app para iOS ou uma Smart TV reutilizam exatamente a mesma lógica.

# 3. Telemetria desacoplada

O Player envia eventos ao Core, e o Core pode encaminhá-los ao Nebula Monitor. Assim, mesmo que o Monitor esteja temporariamente indisponível, a reprodução não é afetada.


---
---

# Arquitetura da Nebula Platform

A Nebula Platform é uma plataforma modular composta por aplicações e serviços independentes. Cada módulo possui responsabilidades claras e se comunica com os demais através de APIs.

O objetivo da arquitetura é separar a reprodução de conteúdo, o gerenciamento das listas e o monitoramento operacional.

---

# Visão Geral

```text
Nebula Player
     │
     │ HTTPS / API
     ▼
Nebula Core
     │
     ├── Banco de Dados
     │
     ├── Painel Administrativo
     │
     └── Nebula Monitor
```

---

# Componentes

## 1. Nebula Player

Aplicativo cliente responsável pela experiência do usuário.

### Responsabilidades

- Exibir a interface do usuário
- Gerar Device Key
- Exibir MAC Address quando disponível
- Solicitar ativação ao Nebula Core
- Solicitar playlist autorizada
- Reproduzir conteúdo
- Enviar eventos de telemetria

### Restrições

- Não armazena conteúdo de mídia
- Não armazena playlists permanentemente
- Não cadastra URLs M3U ou Xtream
- Não possui regras de negócio
- Não decide qual servidor utilizar

---

## 2. Nebula Core

Backend principal da plataforma.

### Responsabilidades

- Autenticação
- Ativação de dispositivos
- Gerenciamento de clientes
- Gerenciamento de dispositivos
- Gerenciamento de playlists
- Gerenciamento de servidores
- Distribuição segura das playlists
- Regras de negócio
- APIs internas e externas

---

## 3. Nebula Admin

Painel administrativo web.

### Responsabilidades

- Cadastrar clientes
- Cadastrar playlists
- Cadastrar servidores
- Vincular playlists a dispositivos
- Ativar dispositivos
- Bloquear dispositivos
- Visualizar métricas
- Visualizar relatórios

---

## 4. Nebula Monitor

Serviço responsável por observabilidade e telemetria.

### Responsabilidades

- Receber heartbeats
- Registrar ping
- Registrar loading
- Registrar buffering
- Registrar erros
- Calcular disponibilidade
- Gerar métricas de QoS
- Alimentar dashboards e alertas

---

## 5. Banco de Dados

Camada de persistência da plataforma.

### Armazena

- Usuários
- Clientes
- Dispositivos
- Playlists
- Servidores
- Eventos de telemetria
- Logs
- Configurações

---

# Fluxo de Ativação

```text
1. Usuário abre o Nebula Player
2. App gera Device Key
3. App identifica MAC Address quando disponível
4. App envia Device Key e MAC ao Nebula Core
5. Nebula Core registra o dispositivo como pendente
6. Administrador acessa o Nebula Admin
7. Administrador vincula uma playlist ao dispositivo
8. Nebula Core marca o dispositivo como ativo
9. Nebula Player consulta novamente o status
10. Nebula Player recebe autorização
```

---

# Fluxo de Reprodução

```text
1. Usuário seleciona um canal no Nebula Player
2. Player solicita ao Nebula Core a playlist autorizada
3. Nebula Core valida o dispositivo
4. Nebula Core identifica a playlist vinculada
5. Nebula Core retorna os dados necessários para reprodução
6. Player inicia a reprodução
7. Player envia eventos de loading, erro e buffering
8. Nebula Monitor registra os eventos
```

---

# Fluxo de Telemetria

```text
Nebula Player
     │
     │ Eventos
     ▼
Nebula Core
     │
     │ Encaminhamento
     ▼
Nebula Monitor
     │
     ▼
Banco de Dados
```

Eventos iniciais:

- App iniciado
- Dispositivo online
- Playlist solicitada
- Canal iniciado
- Loading iniciado
- Loading concluído
- Buffering iniciado
- Buffering concluído
- Erro de reprodução
- App encerrado

---

# Comunicação entre Módulos

## Player → Core

Protocolo:

- HTTPS

Formato:

- JSON

Exemplos:

- Solicitar ativação
- Consultar status do dispositivo
- Solicitar playlist
- Enviar telemetria

---

## Admin → Core

Protocolo:

- HTTPS

Formato:

- JSON

Exemplos:

- Login administrativo
- Cadastro de clientes
- Cadastro de playlists
- Ativação de dispositivos
- Consulta de métricas

---

## Core → Monitor

Protocolo inicial:

- HTTP interno ou fila

Formato:

- JSON

Objetivo:

- Registrar eventos operacionais sem afetar a experiência do usuário.

---

# Princípios Arquiteturais

## Separação de responsabilidades

Cada módulo deve possuir uma responsabilidade clara.

## Cliente leve

O Nebula Player deve conter apenas o necessário para reproduzir conteúdo e se comunicar com a plataforma.

## Centralização das regras de negócio

Toda decisão operacional deve ficar no Nebula Core.

## Observabilidade desacoplada

Falhas no Nebula Monitor não devem impedir a reprodução de conteúdo.

## Segurança por padrão

URLs, credenciais e configurações sensíveis não devem ser expostas ao usuário.

## Evolução modular

A arquitetura deve permitir novos clientes no futuro, como iOS, Apple TV, Tizen e webOS.

---

# Decisões Iniciais

## Plataforma inicial

O MVP terá suporte inicial para:

- Android
- Android TV

---

## Backend

Sugestão inicial:

- Python com FastAPI

Motivos:

- Simplicidade
- Velocidade de desenvolvimento
- Boa documentação
- Facilidade para APIs REST
- Compatibilidade com PostgreSQL e Redis

---

## Banco de Dados

Sugestão inicial:

- PostgreSQL

Motivos:

- Robusto
- Gratuito
- Open source
- Excelente para dados relacionais
- Suporte a JSON quando necessário

---

## Cache e Filas

Sugestão futura:

- Redis

Uso previsto:

- Cache de status
- Sessões
- Filas leves de eventos
- Rate limiting

---

## Painel Administrativo

Sugestão inicial:

- React ou Next.js

---

# Fora do Escopo da Arquitetura v0.1

- Multi-região
- Kubernetes
- Escalabilidade automática
- CDN própria
- Aplicativos iOS
- Aplicativos Tizen/webOS
- Sistema de pagamento
- IA