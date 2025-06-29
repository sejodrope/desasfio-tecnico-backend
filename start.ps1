# Pipeline de Dados EX-001 - ECO+
# Script de inicialização para Windows

Write-Host "🚀 Iniciando Pipeline de Dados EX-001 - ECO+" -ForegroundColor Green
Write-Host "=============================================" -ForegroundColor Green

# Verificar se Docker está rodando
try {
    docker info | Out-Null
    Write-Host "✅ Docker está rodando" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker não está rodando. Por favor, inicie o Docker Desktop." -ForegroundColor Red
    exit 1
}

# Verificar se o arquivo .env existe
if (-not (Test-Path ".env")) {
    Write-Host "📝 Arquivo .env já foi criado com as credenciais fornecidas" -ForegroundColor Yellow
}

Write-Host "✅ Arquivo .env configurado" -ForegroundColor Green

# Parar containers existentes
Write-Host "🛑 Parando containers existentes..." -ForegroundColor Yellow
docker-compose down -v

# Construir e iniciar os serviços
Write-Host "🔨 Construindo e iniciando os serviços..." -ForegroundColor Blue
docker-compose up --build -d

# Aguardar os serviços ficarem prontos
Write-Host "⏳ Aguardando serviços ficarem prontos..." -ForegroundColor Yellow
Start-Sleep -Seconds 30

# Verificar status dos containers
Write-Host "📊 Status dos containers:" -ForegroundColor Cyan
docker-compose ps

# Verificar logs da ingestão
Write-Host ""
Write-Host "📝 Logs recentes da ingestão MQTT:" -ForegroundColor Cyan
docker-compose logs --tail=10 ingestion

# Verificar se o Grafana está acessível
Write-Host ""
Write-Host "🌐 Verificando acesso ao Grafana..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:3000" -UseBasicParsing -TimeoutSec 5 -ErrorAction Stop
    Write-Host "✅ Grafana está acessível em http://localhost:3000" -ForegroundColor Green
    Write-Host "   Usuário: admin / Senha: admin" -ForegroundColor White
} catch {
    Write-Host "❌ Grafana não está acessível ainda" -ForegroundColor Red
}

Write-Host ""
Write-Host "🎯 Sistema inicializado!" -ForegroundColor Green
Write-Host "========================" -ForegroundColor Green
Write-Host "📊 Dashboard OEE: http://localhost:3000" -ForegroundColor White
Write-Host "🔍 Logs em tempo real: docker-compose logs -f" -ForegroundColor White
Write-Host "🛑 Para parar: docker-compose down" -ForegroundColor White
Write-Host ""
Write-Host "💡 Para enviar dados de teste: python test_mqtt.py" -ForegroundColor Yellow

# Abrir o navegador automaticamente
Write-Host "🌐 Abrindo o dashboard no navegador..." -ForegroundColor Blue
Start-Process "http://localhost:3000"
