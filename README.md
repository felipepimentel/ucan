# UCAN - Um Assistente de IA Conversacional

UCAN é um assistente de IA conversacional para ajudar em tarefas de programação, construído com Python e Dear PyGui.

## Características

- Interface moderna e responsiva
- Temas personalizáveis
- Suporte a múltiplas conversas
- Bases de conhecimento integradas
- Integração com modelos de IA

## Requisitos

- Python 3.10 ou superior
- Poetry para gerenciamento de dependências

## Instalação

1. Clone o repositório:
```bash
git clone https://github.com/seu-usuario/ucan.git
cd ucan
```

2. Instale as dependências com Poetry:
```bash
poetry install
```

## Uso

1. Inicie a aplicação:
```bash
poetry run ucan
```

2. Ou execute o exemplo:
```bash
poetry run python examples/chat_app.py
```

## Desenvolvimento

1. Instale as dependências de desenvolvimento:
```bash
poetry install --with dev
```

2. Execute os testes:
```bash
poetry run pytest
```

3. Verifique a qualidade do código:
```bash
poetry run black .
poetry run isort .
poetry run mypy .
poetry run pylint ucan
```

## Estrutura do Projeto

```
ucan/
├── config/           # Configurações
├── core/            # Lógica principal
├── ui/              # Interface do usuário
├── examples/        # Exemplos de uso
├── tests/           # Testes
└── resources/       # Recursos (ícones, temas, etc.)
```

## Contribuindo

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Crie um Pull Request

## Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.