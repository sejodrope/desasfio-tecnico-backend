# Desafio Pipeline de Dados EX-001

## Visão Geral
Este desafio prático visa validar competências de:

1. **Modelagem de Banco de Dados** (PostgreSQL)
2. **Ingestão de Dados via MQTT** com Python (broker MQTT configurado para MQTT)
3. **Visualização de KPIs** em Grafana (ou Power BI)

Os dados de operação da máquina **EX-001** são transmitidos automaticamente a cada 5 minutos por um ambiente MQTT em nuvem. Seu trabalho é **processar** essas informações e **criar** o dashboard de OEE (e demais KPIs).

Você receberá credenciais (host, porta, usuário e senha) para esse ambiente MQTT, que publica mensagens no tópico `ECOPLUS/EX-001/dados`. Seu objetivo é:

- Consumir essas mensagens JSON
- Persisti-las em PostgreSQL
- Criar dashboards com os KPIs abaixo:
  - **Disponibilidade**
  - **Performance** (meta: 100 peças/hora)
  - **Qualidade**
  - **OEE**
  - **Total de peças produzidas**
  - **Total de peças defeituosas**

Para testar e depurar a conexão MQTT, recomendamos instalar o [**MQTT Explorer**](https://mqtt-explorer.com) ou qualquer outro cliente de sua preferência.

## Estrutura do Repositório

```
├── README.md
├── .env.example
├── docker-compose.yml
├── ingestion/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── main.py
├── db/
│   └── init.sql
├── grafana/
│   ├── provisioning/
│   │   ├── datasources/
│   │   │   └── datasources.yml
│   │   └── dashboards/
│   │       └── dashboard_oee.json
└── docs/
├── architecture_diagram.png
└── architecture_diagram.md
```

## Requisitos
- Docker e Docker Compose instalados
- Acesso ao broker MQTT (credenciais serão fornecidas)
- Git
- MQTT Client (opcional, para debug)

## Configuração
1. Copie o arquivo de exemplo de variáveis de ambiente:
    ```bash
    cp .env.example .env
    ```

2. Preencha `MQTT_HOST`, `MQTT_PORT`, `MQTT_USER` e `MQTT_PASS` com as credenciais do broker MQTT:
    ```
    - MQTT_HOST = mqtt.ecoplus-apps.com
    - MQTT_PORT = 1883
    - MQTT_USER = ecoplus-teste:temp_user
    - MQTT_PASS = u9JJ8d8DOp
    ```

## ⚡ Início Rápido

### Opção 1: Script Automatizado (Recomendado)

```powershell
# Windows PowerShell
.\start.ps1
```

```bash
# Linux/macOS
chmod +x start.sh
./start.sh
```

### Opção 2: Manual

```bash
# 1. Configurar ambiente
cp .env.example .env
# (O arquivo .env já está preenchido com as credenciais)

# 2. Iniciar serviços
docker-compose up --build -d

# 3. Verificar logs
docker-compose logs -f ingestion

# 4. Acessar dashboard
# http://localhost:3000 (admin/admin)
```

## Preparação do ambiente

```bash
# Na raiz do projeto
docker-compose up --build
```

Isso irá:

* Iniciar o serviço PostgreSQL e executar o script de criação de tabelas (`db/init.sql`).
* Subir o serviço Python de ingestão, que se conecta ao broker MQTT via MQTT e persiste os dados no banco.
* Executar o Grafana com provisionamento automático de data source.

## Execução

1. Execute o script de inicialização ou siga os passos manuais acima;
2. Aguarde todos os containers subirem (cerca de 30 segundos);
3. Acesse o Grafana em `http://localhost:3000` (usuário/senha: `admin`/`admin`);
4. O dashboard **"Dashboard OEE - Máquina EX-001"** será carregado automaticamente;
5. Os dados reais do MQTT começarão a ser coletados automaticamente;

### 🧪 Teste com Dados de Exemplo (Opcional)

Para gerar dados de teste e validar o funcionamento:

```bash
# Instalar dependências (se necessário)
pip install paho-mqtt python-dotenv

# Executar script de teste
python test_mqtt.py
```

### 📊 Verificar Dados no Banco

```bash
# Conectar ao PostgreSQL
docker-compose exec postgres psql -U admin -d ex001

# Consultar dados recentes
SELECT * FROM dados_maquina ORDER BY datahora DESC LIMIT 10;
```

### 🔍 Monitoramento

```bash
# Logs em tempo real da ingestão
docker-compose logs -f ingestion

# Status dos containers
docker-compose ps

# Parar todos os serviços
docker-compose down
```

6. Aplique seleção de tempo `time picker` nas queries SQL configuradas nos painéis, como no exemplo abaixo:
```sql
SELECT *
FROM dados_maquina
WHERE $__timeFilter(datahora)
```
7. Documente os passos da criação e execução da solução em um arquivo Markdown de forma clara e objetiva;
8. Documente também o resultado final do dashboard (prints e arquivo `.json` de import são bem vindos) e os registros de dados, da forma que preferir;

## KPIs considerados

### A partir dos dados aferidos e registrados, crie um dashboard com os seguintes indicadores:

* **Disponibilidade**: % de tempo em que a máquina esteve pronta para operar (sem paradas, desligamentos e manutenções).
* **Performance**: (peças boas produzidas/hora) ÷ (meta de produção) × 100
* **Qualidade**: (peças boas ÷ peças produzidas) × 100
* **OEE**: Disponibilidade × Performance × Qualidade
* **Total de peças produzidas**: soma de `pecas_produzidas` no intervalo.
* **Total de peças defeituosas**: soma de `pecas_defeituosas` no intervalo.
> Obs: Meta de produção = 100 peças/hora.

#### Mais informações sobre indicadores em [OEE Factors](https://www.oee.com/oee-factors).

---
 
### Demonstre sua capacidade de resolução de problemas e análise de dados com a criação desse dashboard e nos envie os resultados! 
### Encaminhe seu projeto para o seu contato da ECO+, com cópia para rh@ecoautomacao.com.br. 
## Boa sorte!
