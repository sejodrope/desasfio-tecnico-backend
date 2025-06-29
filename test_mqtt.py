import os
import json
import random
from datetime import datetime, timedelta
import paho.mqtt.client as mqtt
from dotenv import load_dotenv

load_dotenv()

# MQTT
MQTT_HOST = os.getenv('MQTT_HOST')
MQTT_PORT = int(os.getenv('MQTT_PORT', 1883))
MQTT_USER = os.getenv('MQTT_USER')
MQTT_PASS = os.getenv('MQTT_PASS')
TOPIC = 'ECOPLUS/EX-001/dados'

def generate_sample_data():
    """Gera dados de exemplo para testar o sistema"""
    
    # Simulando diferentes cenários
    scenarios = [
        # Operação normal
        {"ligada": True, "operacao": True, "manut_cor": False, "manut_prev": False, "producao": (8, 12), "defeitos": (0, 2)},
        # Máquina ligada mas parada
        {"ligada": True, "operacao": False, "manut_cor": False, "manut_prev": False, "producao": (0, 0), "defeitos": (0, 0)},
        # Manutenção preventiva
        {"ligada": True, "operacao": False, "manut_cor": False, "manut_prev": True, "producao": (0, 0), "defeitos": (0, 0)},
        # Manutenção corretiva
        {"ligada": True, "operacao": False, "manut_cor": True, "manut_prev": False, "producao": (0, 0), "defeitos": (0, 0)},
        # Máquina desligada
        {"ligada": False, "operacao": False, "manut_cor": False, "manut_prev": False, "producao": (0, 0), "defeitos": (0, 0)},
    ]
    
    # Escolher cenário baseado em probabilidades
    weights = [70, 10, 8, 7, 5]  # 70% operação normal, etc.
    scenario = random.choices(scenarios, weights=weights)[0]
    
    pecas_produzidas = random.randint(*scenario["producao"])
    pecas_defeituosas = random.randint(*scenario["defeitos"])
    
    # Garantir que defeituosas não seja maior que produzidas
    if pecas_defeituosas > pecas_produzidas:
        pecas_defeituosas = pecas_produzidas
    
    data = {
        "id_maquina": 1,
        "datahora": datetime.now().isoformat(),
        "ligada": scenario["ligada"],
        "operacao": scenario["operacao"],
        "manutencao_corretiva": scenario["manut_cor"],
        "manutencao_preventiva": scenario["manut_prev"],
        "pecas_produzidas": pecas_produzidas,
        "pecas_defeituosas": pecas_defeituosas
    }
    
    return data

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print(f"✅ Conectado ao broker MQTT (código: {rc})")
    else:
        print(f"❌ Falha na conexão MQTT (código: {rc})")

def publish_test_data():
    """Publica dados de teste no broker MQTT"""
    
    client = mqtt.Client()
    client.on_connect = on_connect
    
    try:
        client.username_pw_set(MQTT_USER, MQTT_PASS)
        print(f"🔗 Conectando ao broker: {MQTT_HOST}:{MQTT_PORT}")
        
        client.connect(MQTT_HOST, MQTT_PORT, 60)
        client.loop_start()
        
        # Publicar alguns dados de exemplo
        for i in range(10):
            data = generate_sample_data()
            
            # Variar o timestamp para simular dados históricos
            base_time = datetime.now() - timedelta(minutes=5*i)
            data["datahora"] = base_time.isoformat()
            
            payload = json.dumps(data, ensure_ascii=False)
            
            result = client.publish(TOPIC, payload)
            
            if result.rc == 0:
                print(f"📤 Dados enviados ({i+1}/10): {data}")
            else:
                print(f"❌ Erro ao enviar dados: {result.rc}")
            
        client.loop_stop()
        client.disconnect()
        print("✅ Teste concluído!")
        
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    print("🧪 Iniciando teste de envio de dados MQTT...")
    publish_test_data()
