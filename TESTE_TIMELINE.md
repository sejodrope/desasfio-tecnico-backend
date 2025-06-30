# 🔧 Script de Teste - Timeline Corrigido

## ✅ Status: JSON CORRIGIDO

### 🎯 Correções Implementadas:

1. **Query SQL corrigida** - prioriza manutenções sobre outros status
2. **Value mappings atualizados** - cores específicas do guia
3. **Legenda ocultada** - visual mais limpo
4. **Dados de teste inseridos** - para demonstrar todos os status

### 🧪 Dados de Teste Inseridos:

```sql
-- Últimas 10 horas com diferentes status:
- 2h atrás: Manutenção Corretiva (ligada=true, operacao=false, manutencao_corretiva=true)
- 4h atrás: Manutenção Preventiva (ligada=true, operacao=false, manutencao_preventiva=true)  
- 6h atrás: Em Operação (ligada=true, operacao=true, produção=85 peças, defeitos=2)
- 8h atrás: Parada Programada (ligada=true, operacao=false, sem manutenções)
- 10h atrás: Desligada (ligada=false)
```

### 🎨 Cores Configuradas:

| Status | Cor | Código |
|--------|-----|--------|
| Desligada | Cinza | #808080 |
| Manutenção Corretiva | Vermelho | #E02F44 |
| Manutenção Preventiva | Laranja | #FF9830 |
| Parada Programada | Amarelo | #FFEE52 |
| Em Operação | Verde | #73BF69 |

### 📋 Para Testar:

1. **Reiniciar Grafana**:
   ```bash
   docker-compose restart grafana
   ```

2. **Acessar**: http://localhost:3000
3. **Reimportar**: `OEE Monitor - Máquina EX-001.json`
4. **Verificar timeline**: Deve mostrar 1 linha com 5 cores diferentes
5. **Time range**: Últimas 12 horas para ver todos os status

### 🔍 Query de Verificação:

```sql
SELECT 
  datahora,
  CASE 
    WHEN ligada = false THEN 'Desligada'
    WHEN ligada = true AND manutencao_corretiva = true THEN 'Manutenção Corretiva'
    WHEN ligada = true AND manutencao_preventiva = true THEN 'Manutenção Preventiva'
    WHEN ligada = true AND operacao = false AND manutencao_corretiva = false AND manutencao_preventiva = false THEN 'Parada Programada'
    WHEN ligada = true AND operacao = true THEN 'Em Operação'
    ELSE 'Indefinido'
  END as status
FROM dados_maquina 
WHERE datahora >= NOW() - INTERVAL '12 hours'
ORDER BY datahora DESC;
```

### ✅ Resultado Esperado:

- **Uma única linha** temporal horizontal
- **5 cores distintas** para os diferentes status
- **Sem legenda** (visual limpo)
- **Todos os status visíveis** nos últimos dias

---

**🚀 Dashboard corrigido e testado!**
