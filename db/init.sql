CREATE TABLE IF NOT EXISTS dados_maquina (
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

CREATE INDEX IF NOT EXISTS idx_dados_maquina_datahora
  ON dados_maquina(datahora);