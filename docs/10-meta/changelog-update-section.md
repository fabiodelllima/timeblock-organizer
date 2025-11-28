# Adicionar ao changelog.md em [Não Lançado]

## [Não Lançado]

### Em Desenvolvimento

- Correção de testes falhando (Categoria 1 concluída)
- Limpeza de documentação obsoleta

### Deprecated

- `schedule generate` - Usar `habit create --generate N` (ver deprecation-notices.md)
- `list --weeks` - Usar `list --week +N` (ver deprecation-notices.md)
- `habit adjust` - Usar `habit edit` (ver deprecation-notices.md)

### Alterado

- `list` API simplificada: `--week` agora aceita ranges (+N/-N)
- `habit create` agora suporta `--generate N` para geração automática

### Corrigido

- Bug em routine.py: session.commit() faltando em create/activate/deactivate/delete
- Testes de integração usando fixture sem rotina ativa

### Adicionado

- `docs/10-meta/deprecation-notices.md` - Registro centralizado de APIs depreciadas
- `docs/10-meta/archived/` - Diretório para documentação obsoleta
