import os
import json
import logging
import time
from datetime import datetime
from sqlalchemy import create_engine, text
import paho.mqtt.client as mqtt
from dotenv import load_dotenv

load_dotenv()

# MQTT
MQTT_HOST = os.getenv('MQTT_HOST')
MQTT_PORT = int(os.getenv('MQTT_PORT', 1883))
MQTT_USER = os.getenv('MQTT_USER')
MQTT_PASS = os.getenv('MQTT_PASS')
TOPIC = 'ECOPLUS/EX-001/dados'

# PostgreSQL
DB_URL = f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@{os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT')}/{os.getenv('POSTGRES_DB')}"

# Configuração de logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Tentativa de conexão com retry
def create_db_connection():
    max_retries = 5
    retry_delay = 5
    
    for attempt in range(max_retries):
        try:
            engine = create_engine(DB_URL)
            # Teste a conexão
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            logger.info(f"✅ Conexão com PostgreSQL estabelecida: {DB_URL}")
            return engine
        except Exception as e:
            logger.warning(f"❌ Tentativa {attempt + 1}/{max_retries} falhou: {e}")
            if attempt < max_retries - 1:
                logger.info(f"⏳ Aguardando {retry_delay}s antes da próxima tentativa...")
                time.sleep(retry_delay)
            else:
                logger.error("❌ Não foi possível conectar ao PostgreSQL após todas as tentativas")
                raise

engine = create_db_connection()

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        logger.info(f"✅ Conectado ao broker MQTT (código: {rc})")
        client.subscribe(TOPIC)
        logger.info(f"📡 Inscrito no tópico: {TOPIC}")
    else:
        logger.error(f"❌ Falha na conexão MQTT (código: {rc})")

def on_message(client, userdata, msg):
    try:
        logger.info(f"📨 Mensagem recebida no tópico: {msg.topic}")
        payload = json.loads(msg.payload.decode())
        logger.info(f"📄 Payload: {payload}")
        
        # Validação dos campos obrigatórios
        required_fields = ['id_maquina', 'datahora', 'ligada', 'operacao', 
                          'manutencao_corretiva', 'manutencao_preventiva', 
                          'pecas_produzidas', 'pecas_defeituosas']
        
        for field in required_fields:
            if field not in payload:
                raise ValueError(f"Campo obrigatório ausente: {field}")
        
        # Campos esperados
        id_maquina = payload['id_maquina']
        datahora = datetime.fromisoformat(payload['datahora'].replace('Z', '+00:00'))
        ligada = payload['ligada']
        operacao = payload['operacao']
        manut_cor = payload['manutencao_corretiva']
        manut_prev = payload['manutencao_preventiva']
        p_boas = payload['pecas_produzidas']
        p_refugo = payload['pecas_defeituosas']

        insert = text("""
            INSERT INTO dados_maquina(
              id_maquina, datahora, ligada, operacao,
              manutencao_corretiva, manutencao_preventiva,
              pecas_produzidas, pecas_defeituosas
            ) VALUES (
              :id_maquina, :datahora, :ligada, :operacao,
              :manut_cor, :manut_prev,
              :p_boas, :p_refugo
            )
        """)
        
        with engine.begin() as conn:
            conn.execute(insert, {
                'id_maquina': id_maquina,
                'datahora': datahora,
                'ligada': ligada,
                'operacao': operacao,
                'manut_cor': manut_cor,
                'manut_prev': manut_prev,
                'p_boas': p_boas,
                'p_refugo': p_refugo
            })
            
        logger.info(f"✅ Dados inseridos com sucesso: máquina {id_maquina} @ {datahora}")
        logger.info(f"📊 Peças produzidas: {p_boas}, Defeituosas: {p_refugo}")
        
    except json.JSONDecodeError as e:
        logger.error(f"❌ Erro ao decodificar JSON: {e}")
    except ValueError as e:
        logger.error(f"❌ Erro de validação: {e}")
    except Exception as e:
        logger.error(f"❌ Erro ao inserir dados no banco: {e}")

def on_disconnect(client, userdata, rc):
    if rc != 0:
        logger.warning(f"⚠️ Desconectado inesperadamente do MQTT (código: {rc})")
    else:
        logger.info("👋 Desconectado do MQTT")

def main():
    logger.info("🚀 Iniciando serviço de ingestão MQTT...")
    logger.info(f"🔗 Broker MQTT: {MQTT_HOST}:{MQTT_PORT}")
    logger.info(f"👤 Usuário: {MQTT_USER}")
    logger.info(f"📡 Tópico: {TOPIC}")
    
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_disconnect = on_disconnect
    
    try:
        client.username_pw_set(MQTT_USER, MQTT_PASS)
        logger.info("🔐 Credenciais MQTT configuradas")
        
        client.connect(MQTT_HOST, MQTT_PORT, 60)
        logger.info("📞 Tentando conectar ao broker MQTT...")
        
        client.loop_forever()
        
    except KeyboardInterrupt:
        logger.info("⏹️ Interrupção pelo usuário")
    except Exception as e:
        logger.error(f"❌ Erro na conexão MQTT: {e}")
    finally:
        client.disconnect()
        logger.info("👋 Serviço finalizado")

if __name__ == '__main__':
    main()