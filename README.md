# UCAN Chat

Um aplicativo de chat moderno e elegante desenvolvido com Python e CustomTkinter.

## Características

- Interface moderna e responsiva
- Suporte a emojis
- Configurações de perfil
- Histórico de mensagens
- Temas claro e escuro
- Notificações
- Som

## Requisitos

- Python 3.9 ou superior
- Poetry para gerenciamento de dependências

## Instalação

1. Clone o repositório:
```bash
git clone https://github.com/pimenta/ucan.git
cd ucan
```

2. Instale as dependências com Poetry:
```bash
poetry install
```

## Execução

Para executar o aplicativo:

```bash
poetry run ucan
```

## Estrutura do Projeto

```
ucan/
├── __init__.py
├── main.py
├── chat.py
├── ui.py
├── constants.py
└── helpers.py
```

- `main.py`: Ponto de entrada e lógica principal
- `chat.py`: Lógica do chat e mensagens
- `ui.py`: Componentes da interface
- `constants.py`: Constantes e configurações
- `helpers.py`: Funções utilitárias

## Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.