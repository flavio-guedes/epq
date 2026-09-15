# Padrão Operacional — GitHub e Deploy

## Objetivo
Fluxo confiável e repetível:
`Desenvolvimento local → Validação → Git → GitHub → Build → Deploy → Produção`

## Checklist pré-deploy
- [ ] `gh auth status`
- [ ] `git status --short --branch`
- [ ] remotes válidos
- [ ] branch correta
- [ ] `.gitmodules` sincronizado ou ausente
- [ ] sem segredos versionados
- [ ] variáveis apenas no provedor de deploy
- [ ] build local ok
- [ ] diff contra `origin/<branch>` revisado

## Padrão de branches
- branch principal: `main`
- branches de trabalho: `feat/*`, `fix/*`
- mescla via PR

## Padrão de commits
Conventional Commits:
- `feat:` funcionalidade
- `fix:` correção
- `chore:` manutenção
- `docs:` documentação
- `refactor:` refatoração
- `ci:` pipeline/actions

## Procedimento de rollback
1. identificar commit atual em produção
2. `git revert <commit>` ou reset para o commit anterior desejado
3. push + deploy
4. registrar motivo e horário

## Pós-deploy
- [ ] site retorna 200
- [ ] CI verde
- [ ] deploy/build status ok
- [ ] smoke test funcional
