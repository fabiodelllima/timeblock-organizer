# 1. Introdução e Metas

## Requisitos

**Problema:** Gerenciamento manual de agenda é ineficiente e propenso a conflitos.

**Solução:** CLI que:

- Gerencia hábitos recorrentes
- Detecta conflitos automaticamente
- Reordena eventos por prioridade
- Rastreia tempo real vs planejado

## Objetivos de Qualidade

| Atributo       | Meta                    | Métrica              |
| -------------- | ----------------------- | -------------------- |
| Performance    | Reordering rápido       | < 100ms (50 eventos) |
| Confiabilidade | Zero perda de dados     | 100% transações ACID |
| Usabilidade    | Curva aprendizado baixa | < 15min primeiro uso |
| Testabilidade  | Alta cobertura          | > 90%                |

## Stakeholders

- **Usuário Final:** Pessoa organizando tempo
- **Desenvolvedor:** Mantenedor do sistema
