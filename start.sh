#!/bin/bash

echo "🚀 Iniciando Pipeline de Dados EX-001 - ECO+"
echo "============================================="

# Verificar se Docker está rodando
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker não está rodando. Por favor, inicie o Docker Desktop."
    exit 1
fi

echo "✅ Docker está rodando"

# Verificar se o arquivo .env existe
if [ ! -f .env ]; then
    echo "❌ Arquivo .env não encontrado. Criando com credenciais padrão..."
    cp .env.example .env
    # Preencher com as credenciais fornecidas
    sed -i 's/MQTT_HOST=/MQTT_HOST=mqtt.ecoplus-apps.com/' .env
    sed -i 's/MQTT_PORT=/MQTT_PORT=1883/' .env
    sed -i 's/MQTT_USER=/MQTT_USER=ecoplus-teste:temp_user/' .env
    sed -i 's/MQTT_PASS=/MQTT_PASS=u9JJ8d8DOp/' .env
fi

echo "✅ Arquivo .env configurado"

# Parar containers existentes
echo "🛑 Parando containers existentes..."
docker-compose down -v

# Construir e iniciar os serviços
echo "🔨 Construindo e iniciando os serviços..."
docker-compose up --build -d

# Aguardar os serviços ficarem prontos
echo "⏳ Aguardando serviços ficarem prontos..."
sleep 30

# Verificar status dos containers
echo "📊 Status dos containers:"
docker-compose ps

# Verificar logs da ingestão
echo ""
echo "📝 Logs recentes da ingestão MQTT:"
docker-compose logs --tail=10 ingestion

# Verificar se o Grafana está acessível
echo ""
echo "🌐 Verificando acesso ao Grafana..."
if curl -s http://localhost:3000 > /dev/null; then
    echo "✅ Grafana está acessível em http://localhost:3000"
    echo "   Usuário: admin / Senha: admin"
else
    echo "❌ Grafana não está acessível"
fi

echo ""
echo "🎯 Sistema inicializado!"
echo "========================"
echo "📊 Dashboard OEE: http://localhost:3000"
echo "🔍 Logs em tempo real: docker-compose logs -f"
echo "🛑 Para parar: docker-compose down"
echo ""
echo "💡 Para enviar dados de teste: python test_mqtt.py"
