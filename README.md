# Solução do Desafio Técnico - Pipeline de Dados EX-001

## 🎯 Objetivo

Desenvolver um pipeline completo para monitoramento de OEE (Overall Equipment Effectiveness) da máquina EX-001, incluindo:

- ✅ Ingestão de dados via MQTT
- ✅ Armazenamento em PostgreSQL  
- ✅ Visualização de KPIs no Grafana

## 🏗️ Arquitetura da Solução

```
MQTT Broker ──→ Python Ingestion ──→ PostgreSQL ──→ Grafana Dashboard
(EcoPlus)       (Container)           (Container)     (Container)
```

### Componentes:

1. **MQTT Broker Externo**: `mqtt.ecoplus-apps.com`
2. **Serviço de Ingestão**: Container Python com paho-mqtt
3. **Banco de Dados**: PostgreSQL com esquema otimizado
4. **Visualização**: Grafana com dashboard OEE pré-configurado

## 🚀 Como Executar

### 1. Configuração Inicial

```bash
# Clone o repositório (se necessário)
git clone https://github.com/sejodrope/desasfio-tecnico-backend
cd desafio-tecnico-backend

# O arquivo .env já está configurado com as credenciais fornecidas
```

### 2. Iniciar os Serviços

```bash
# Construir e iniciar todos os containers
docker-compose up --build

# Para executar em background
docker-compose up --build -d
```

### 3. Verificar os Serviços

- **PostgreSQL**: Porta 5432
- **Grafana**: http://localhost:3000 (admin/ecoadmin)
- **Logs de Ingestão**: `docker-compose logs ingestion`


## 📊 KPIs Implementados

O dashboard do Grafana inclui todos os KPIs solicitados:

### 1. **Disponibilidade** 🟢
- **Fórmula**: `(Tempo sem paradas / Tempo total) × 100`
- **Critério**: Máquina ligada, sem manutenções
- **Meta**: > 85% (verde), 70-85% (amarelo), < 70% (vermelho)

### 2. **Performance** 🔵  
- **Fórmula**: `(Peças boas/hora / Meta produção) × 100`
- **Meta de Produção**: 100 peças/hora
- **Critério**: Apenas durante operação ativa

### 3. **Qualidade** 🟡
- **Fórmula**: `(Peças boas / Peças produzidas) × 100`
- **Meta**: > 95% (verde), 90-95% (amarelo), < 90% (vermelho)

### 4. **OEE** 🏆
- **Fórmula**: `Disponibilidade × Performance × Qualidade`
- **Benchmark**: > 85% (classe mundial), 60-85% (bom), < 60% (precisa melhorar)

### 5. **Totalizadores** 📈
- **Total de Peças Produzidas**: Soma no período selecionado
- **Total de Peças Defeituosas**: Soma no período selecionado

### 6. **Gráficos Temporais** 📉
- **Status da Máquina**: Timeline com estados (operação, manutenção, parada, desligada)
- **Produção por Hora**: Barras com produção total, defeituosas e boas
- **Eficiência por Período**: Qualidade % e performance por hora

## 🔧 Detalhes Técnicos

### Estrutura do Banco de Dados

```sql
CREATE TABLE dados_maquina (
  id SERIAL PRIMARY KEY,
  id_maquina INTEGER NOT NULL,
  datahora TIMESTAMPTZ NOT NULL,
  ligada BOOLEAN,
  operacao BOOLEAN,
  manutencao_corretiva BOOLEAN,
  manutencao_preventiva BOOLEAN,
  pecas_produzidas INTEGER,
  pecas_defeituosas INTEGER
);

-- Índice para otimizar consultas temporais
CREATE INDEX idx_dados_maquina_datahora ON dados_maquina(datahora);
```

### Formato das Mensagens MQTT

```json
{
  "id_maquina": 1,
  "datahora": "2025-01-01T12:00:00-03:00",
  "ligada": true,
  "operacao": true,
  "manutencao_corretiva": false,
  "manutencao_preventiva": false,
  "pecas_produzidas": 9,
  "pecas_defeituosas": 1
}
```

### Melhorias Implementadas

1. **Logs Detalhados**: Emojis e informações claras sobre o processo
2. **Validação de Dados**: Verificação de campos obrigatórios
3. **Tratamento de Erros**: Retry automático para conexão DB
4. **Tolerância a Falhas**: Reconexão automática MQTT
5. **Timezone**: Suporte a fuso horário brasileiro
6. **Dashboard Responsivo**: Interface otimizada para diferentes telas

## 📈 Queries SQL dos KPIs

### Disponibilidade
```sql
WITH tempo_total AS (
  SELECT EXTRACT(EPOCH FROM (MAX(datahora) - MIN(datahora))) / 3600 AS horas_periodo
  FROM dados_maquina WHERE $__timeFilter(datahora)
),
tempo_disponivel AS (
  SELECT EXTRACT(EPOCH FROM SUM(
    CASE 
      WHEN ligada = true AND manutencao_corretiva = false AND manutencao_preventiva = false 
      THEN INTERVAL '5 minutes'
      ELSE INTERVAL '0'
    END
  )) / 3600 AS horas_disponivel
  FROM dados_maquina WHERE $__timeFilter(datahora)
)
SELECT 
  CASE 
    WHEN tt.horas_periodo > 0 
    THEN ROUND((td.horas_disponivel / tt.horas_periodo * 100)::numeric, 2)
    ELSE 0
  END AS disponibilidade
FROM tempo_total tt, tempo_disponivel td;
```

### Performance
```sql
WITH producao_real AS (
  SELECT 
    SUM(pecas_produzidas - pecas_defeituosas) AS pecas_boas,
    EXTRACT(EPOCH FROM (MAX(datahora) - MIN(datahora))) / 3600 AS horas_periodo
  FROM dados_maquina 
  WHERE $__timeFilter(datahora) AND operacao = true
)
SELECT 
  CASE 
    WHEN horas_periodo > 0 
    THEN ROUND(((pecas_boas / horas_periodo) / 100 * 100)::numeric, 2)
    ELSE 0
  END AS performance
FROM producao_real;
```

### Qualidade
```sql
WITH qualidade_calc AS (
  SELECT 
    SUM(pecas_produzidas) AS total_produzidas,
    SUM(pecas_produzidas - pecas_defeituosas) AS pecas_boas
  FROM dados_maquina 
  WHERE $__timeFilter(datahora)
)
SELECT 
  CASE 
    WHEN total_produzidas > 0 
    THEN ROUND((pecas_boas::float / total_produzidas * 100)::numeric, 2)
    ELSE 0
  END AS qualidade
FROM qualidade_calc;
```

## 🎨 Dashboard Features

- **Refresh Automático**: 30 segundos
- **Time Picker**: Seleção flexível de período
- **Cores Semafóricas**: Verde/Amarelo/Vermelho baseado em thresholds
- **Tooltips Informativos**: Detalhes sobre cada métrica
- **Layouts Responsivos**: Adaptação a diferentes resoluções

## 🔍 Monitoramento e Debug

### Verificar Logs dos Containers

```bash
# Logs da ingestão MQTT
docker-compose logs -f ingestion

# Logs do PostgreSQL
docker-compose logs -f postgres

# Logs do Grafana
docker-compose logs -f grafana
```

### Verificar Dados no Banco

```bash
# Conectar ao PostgreSQL
docker-compose exec postgres psql -U admin -d ex001

# Consultar dados recentes
SELECT * FROM dados_maquina ORDER BY datahora DESC LIMIT 10;

# Verificar contagem de registros
SELECT COUNT(*) FROM dados_maquina;
```

### Testar Conexão MQTT

Use o **MQTT Explorer** ou cliente similar:
- **Host**: mqtt.ecoplus-apps.com
- **Port**: 1883
- **Username**: ecoplus-teste:temp_user
- **Password**: u9JJ8d8DOp
- **Topic**: ECOPLUS/EX-001/dados

## 🚨 Troubleshooting

### Problema: Containers não iniciam
```bash
# Verificar logs
docker-compose logs

# Recriar containers
docker-compose down -v
docker-compose up --build
```

### Problema: Não recebe dados MQTT
1. Verificar credenciais no `.env`
2. Testar conectividade com MQTT Explorer
3. Verificar logs do container ingestion

### Problema: Dashboard vazio
1. Verificar se há dados no banco (executar a query)
2. Ajustar time range no Grafana
3. Verificar conexão do datasource PostgreSQL


---

**Desenvolvido por**: José Pedro  
**Desafio**: ECO+ Automação - Vaga Backend
