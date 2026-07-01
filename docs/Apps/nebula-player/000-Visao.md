# 1. Nebula Player

O **Nebula Player** é o cliente oficial da Nebula Platform, responsável exclusivamente pela experiência de reprodução do usuário.

Seu papel é consumir as informações disponibilizadas pelo **Nebula Core** e apresentar o conteúdo de forma simples, rápida e estável.

## Responsabilidades

- Reprodução de playlists
- Interface gráfica (UI)
- Login e ativação do dispositivo
- Troca de canais
- Gerenciamento de favoritos
- Configurações do aplicativo
- Comunicação com o Nebula Core através das APIs

## O que o Nebula Player NÃO faz

- Não armazena playlists M3U.
- Não armazena credenciais Xtream.
- Não decide qual servidor utilizar.
- Não gerencia clientes.
- Não gerencia dispositivos.
- Não realiza monitoramento.
- Não possui regras de negócio.
- Não armazena conteúdo de mídia.
- Não distribui conteúdo.

## Funcionamento

Sempre que necessário, o Nebula Player consulta o Nebula Core para obter:

- Playlist autorizada para o dispositivo
- Configurações
- Permissões
- Informações de atualização
- Recursos habilitados

Após receber essas informações, o Player realiza apenas a reprodução do conteúdo autorizado.

O Nebula Player atua como um cliente de reprodução, enquanto toda a inteligência da plataforma permanece centralizada no Nebula Core.

---

Princípio da Centralização

Toda decisão operacional pertence ao Nebula Core.

O Nebula Player é um cliente de reprodução e interface. Ele nunca deve armazenar informações críticas de forma permanente nem conter regras de negócio.

Essa filosofia garante que:

alterações de configuração ocorram de forma centralizada;
dispositivos possam ser ativados, bloqueados ou reconfigurados remotamente;
o comportamento da plataforma permaneça consistente em todas as plataformas (Android, Android TV, iOS, Apple TV, Tizen e webOS).