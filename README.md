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

## 📥 Instalação e Configuração

### 1. Download do Repositório

```bash
# Opção 1: Via Git Clone
git clone https://github.com/sejodrope/desafio-tecnico-backend.git
cd desafio-tecnico-backend

# Opção 2: Download ZIP
# Acesse: https://github.com/sejodrope/desafio-tecnico-backend
# Clique em "Code" > "Download ZIP"
# Extraia o arquivo e navegue até a pasta do projeto
```

### 2. Iniciar os Serviços

```bash
# Construir e iniciar todos os containers
docker-compose up --build

# Para executar em background
docker-compose up --build -d
```

### 3. Aguardar Inicialização

Aguarde alguns segundos para que todos os serviços sejam iniciados. Você pode verificar o status com:

```bash
docker-compose ps
```

### 4. Importar Dashboard no Grafana

#### Passo 1: Acessar o Grafana
- Abra o navegador e acesse: http://localhost:3000
- **Usuário**: `admin`
- **Senha**: `ecoadmin`

#### Passo 2: Importar o Dashboard
1. No menu lateral esquerdo, clique no ícone **"+"** (Create)
2. Selecione **"Import"**
3. Clique em **"Upload JSON file"**
4. Selecione o arquivo `OEE Monitor - Máquina EX-001.json` da pasta do projeto
5. Clique em **"Import"**

#### Passo 3: Configurar Datasource (se necessário)
Se solicitado, configure o datasource PostgreSQL:
- **Name**: `PostgreSQL`
- **Host**: `postgres:5432`
- **Database**: `ex001`
- **User**: `admin`
- **Password**: `ecoadmin123`
- **SSL Mode**: `disable`

#### Passo 4: Verificar Dashboard
Após a importação, o dashboard "OEE Monitor - Máquina EX-001" estará disponível e começará a exibir dados automaticamente.

### 5. Verificar os Serviços

- **PostgreSQL**: Porta 5432
- **Grafana**: http://localhost:3000 (admin/ecoadmin)
- **Logs de Ingestão**: `docker-compose logs ingestion`

## 🔧 Alternativa - Importação via Upload JSON

Se preferir, você também pode importar o dashboard copiando o conteúdo JSON:

1. Abra o arquivo `OEE Monitor - Máquina EX-001.json` em um editor de texto
2. Copie todo o conteúdo JSON
3. No Grafana, vá em **Create > Import**
4. Cole o JSON na área de texto **"Import via panel json"**
5. Clique em **"Load"** e depois **"Import"**

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

### Problema: Erro na importação do dashboard
1. Verificar se o arquivo JSON está na pasta correta
2. Tentar a importação via cópia do conteúdo JSON
3. Verificar se o datasource PostgreSQL está configurado corretamente

## 🔧 Correções Recentes (v2.0)

**Feedback ECO+ implementado (30/06/2025):**

1. ✅ **Linha do Tempo**: Inclui todos os status (manutenções, paradas, operação)
2. ✅ **Produção vs Meta**: Meta como linha de referência ao invés de empilhamento
3. ✅ **Visual Melhorado**: Cores intuitivas e comparação facilitada

**Principais melhorias:**
- Timeline com cores distintas para cada status da máquina
- Gráfico de produção com meta como linha tracejada vermelha
- Separação visual clara entre peças boas e defeituosas
- Remoção do empilhamento confuso no gráfico de barras

Veja detalhes completos em: `CORREÇÕES_DASHBOARD.md`

---

**Desenvolvido por**: José Pedro  
**Desafio**: ECO+ Automação - Vaga Backend