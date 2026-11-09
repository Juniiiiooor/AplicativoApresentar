## Resumo

Descreva o que foi feito e por quê.

## Tipo de mudança

- [ ] Correção de bug
- [ ] Nova funcionalidade
- [ ] Refatoração
- [ ] Documentação
- [ ] Testes / CI

## Como testar

```powershell
python -m unittest discover -s tests -v
cd backend
pytest -q
cd ../web
npm run build
```

## Checklist

- [ ] Os testes do núcleo passam
- [ ] Os testes da API passam
- [ ] O build do front-end passa
- [ ] Atualizei o README quando necessário
- [ ] Não commitei `data/ranking.json`, `node_modules` ou `dist`
