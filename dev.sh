# GERAR TODO SETUP DE PREPARACAO DE AMBIENTE

### python3 -m venv venv

### source venv/bin/activate

### pip install --upgrade pip

### pip install -r requirements.txt

#!/bin/bash

set -e  # para o script se der erro

echo "🐍 Criando ambiente virtual..."
python3 -m venv venv

echo "🔌 Ativando ambiente virtual..."
source venv/bin/activate

echo "⬆️ Atualizando pip..."
pip install --upgrade pip

echo "📦 Instalando dependências..."
pip install -r requirements.txt

echo "✅ Ambiente pronto!"