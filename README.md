# UCAN - Universal Conversational Assistant Network

UCAN é uma aplicação desktop moderna para interação com modelos de linguagem de última geração.

## Características

- Interface gráfica moderna e intuitiva
- Suporte a múltiplos modelos de linguagem
- Gerenciamento de conversas
- Exportação e importação de conversas
- Temas claro e escuro
- Hot reload para desenvolvimento

## Requisitos

- Python 3.10 ou superior
- Poetry para gerenciamento de dependências

## Instalação

1. Clone o repositório:
```bash
git clone https://github.com/seu-usuario/ucan.git
cd ucan
```

2. Instale as dependências usando Poetry:
```bash
poetry install
```

## Uso

Execute a aplicação:
```bash
poetry run python -m ucan
```

## Desenvolvimento

### Configuração do Ambiente

1. Instale as dependências de desenvolvimento:
```bash
poetry install --with dev
```

2. Configure o pre-commit:
```bash
poetry run pre-commit install
```

### Comandos Úteis

- Formatar código:
```bash
poetry run black ucan
poetry run isort ucan
```

- Verificar tipos:
```bash
poetry run mypy ucan
```

- Executar testes:
```bash
poetry run pytest
```

## Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.