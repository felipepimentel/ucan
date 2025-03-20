# UCAN Cursor Rules

Este diretório contém as regras para o assistente de IA do Cursor que auxiliam no desenvolvimento do projeto UCAN. As regras funcionam como instruções para o modelo de linguagem, ajudando a manter a consistência e a qualidade do código.

## O que são as regras do Cursor?

As regras do Cursor são arquivos `.mdc` que contêm instruções específicas para o assistente de IA. Cada regra inclui:

- **description**: Uma descrição clara do propósito da regra
- **globs**: Padrões de arquivos aos quais a regra se aplica
- **alwaysApply**: Se a regra deve ser aplicada sempre ou apenas em contextos específicos

## Regras Disponíveis

1. **duplication_prevention.mdc**: Regras para prevenir duplicação de código, garantindo que componentes existentes sejam reutilizados.
2. **component_registry.mdc**: Diretrizes para documentar componentes em registros centralizados.
3. **change_workflow.mdc**: Processo para planejar, implementar e validar mudanças no código.
4. **tools.mdc**: Ferramentas recomendadas para verificar e manter a qualidade do código.
5. **architectural_decisions.mdc**: Regras para documentar decisões arquiteturais importantes (ADRs).
6. **terminology.mdc**: Diretrizes para manter uma terminologia consistente através de um glossário.
7. **contextual_documentation.mdc**: Práticas para adicionar contexto à documentação de código.
8. **dependency_management.mdc**: Regras para gerenciar e documentar dependências externas.
9. **context_continuity.mdc**: Estratégias para manter contexto entre sessões de desenvolvimento.

## Como Funcionam as Regras

O assistente de IA do Cursor aplica automaticamente as regras quando você trabalha com arquivos que correspondem aos padrões definidos. Por exemplo:

- Ao editar um arquivo Python em `ucan/ui/`, o assistente aplicará as regras relevantes baseadas nos globs definidos
- As regras com `alwaysApply: true` serão aplicadas em todos os contextos
- As regras podem ser encadeadas usando referências a outros arquivos de regra

## Mecanismos de Controle

Para garantir que o projeto não cresça de maneira desorganizada, implementamos vários mecanismos de controle:

### 1. Prevenção de Duplicação
- Regras específicas para buscar código similar antes de criar novos componentes
- Script automatizado `scripts/check_duplication.py` para detectar código duplicado
- Processo de verificação de componentes existentes antes de implementar novos

### 2. Registro de Componentes
- Arquivos de registro centralizados que documentam todos os componentes disponíveis
- Processo para adicionar novos componentes aos registros
- Consulta obrigatória aos registros antes de criar novos componentes

### 3. Fluxo de Trabalho para Alterações
- Processo estruturado para planejar e implementar mudanças
- Checklist de implementação para garantir qualidade e consistência
- Estratégias claras para extensão, composição e refatoração

### 4. Ferramentas Automatizadas
- Conjunto de ferramentas para verificar a qualidade do código
- Hooks de pre-commit para executar verificações antes de cada commit
- Configuração para integração contínua

### 5. Documentação de Decisões Arquiteturais
- Sistema de ADRs (Architectural Decision Records) para documentar decisões importantes
- Rastreabilidade entre decisões arquiteturais e implementações
- Referências cruzadas entre código e documentação

### 6. Continuidade de Contexto
- Registro de sessões de desenvolvimento
- Diário de desenvolvimento para acompanhar a evolução do projeto
- Práticas específicas para trabalhar com assistentes de IA

### 7. Gestão de Terminologia
- Glossário centralizado para garantir consistência em nomes e conceitos
- Revisão periódica da terminologia
- Referências ao glossário no código e documentação

### 8. Documentação Contextual
- Docstrings enriquecidas com informações de contexto
- Comentários que explicam o "por quê" além do "como"
- Referências a documentação externa e ADRs

### 9. Gestão de Dependências
- Documentação clara sobre cada dependência externa
- Camadas de abstração para desacoplar o código de bibliotecas específicas
- Processo para avaliar e adicionar novas dependências

## Editando as Regras

Para editar uma regra existente ou adicionar uma nova:

1. Modificar/criar o arquivo `.mdc` na pasta `.cursor/rules/`
2. Seguir o formato:
   ```markdown
   ---
   description: Descrição da regra
   globs: "padrão/de/arquivos/*"
   alwaysApply: true/false
   ---

   Conteúdo da regra...
   ```

3. Reiniciar o Cursor para que as mudanças sejam aplicadas

## Benefícios

- **Consistência**: Mantém padrões consistentes em todo o código
- **Onboarding**: Ajuda novos colaboradores a entender os padrões do projeto
- **Qualidade**: Promove boas práticas de desenvolvimento
- **Eficiência**: Reduz a necessidade de revisões repetitivas
- **Prevenção de Duplicação**: Evita a criação de componentes redundantes
- **Crescimento Controlado**: Garante que o projeto cresça de forma organizada
- **Continuidade**: Preserva o contexto entre diferentes sessões de desenvolvimento
- **Manutenção do Contexto**: Garante que a IA e os desenvolvedores mantenham o conhecimento do sistema

As regras do Cursor, junto com os mecanismos de controle implementados, ajudam a garantir que o projeto UCAN cresça de maneira saudável e sustentável, mesmo com múltiplos colaboradores e assistência de IA. 