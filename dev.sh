#!/bin/bash

### ======================================== Variables ======================================== ###
# Path to backend
BACKEND_DIR="backend"
# Path to frontend
FRONTEND_DIR="frontend/theme-creator/"
# Detects the running OS
OS_TYPE=$(uname)
# Get the name of the logged user
USERNAME="$USER"
USERNAME_FORMATTED="$(echo "${USERNAME:0:1}" | tr '[:lower:]' '[:upper:]')$(echo "${USERNAME:1}" | tr '[:upper:]' '[:lower:]')"
UI_SEP=$(printf '%*s' "$(tput cols)" '' | tr ' ' '=')
# Get the absolute path of the current directory
BASE_DIR=$(pwd)

DATE_HOUR=$(date +"%Y-%m-%d %H:%M:%S")

echo $UI_SEP
echo 'PREPARING SUPERNANNO SETUP'
echo $UI_SEP
echo 'User Name:' $USERNAME_FORMATTED'' 
echo 'Date:' $DATE_HOUR
echo 'OS:' $OS_TYPE
echo $UI_SEP
echo ""

if [ ! -d "venv" ]; then
    echo $UI_SEP
    echo "SETTING UP VIRTUAL ENVIRONMENT"
    echo $UI_SEP
    echo "[ 🐍 ]: Creating virtual environment..."
    python3 -m venv venv
else
    echo $UI_SEP
    echo "[ DONE ]: SETTING UP VIRTUAL ENVIRONMENT"
    echo $UI_SEP
    echo "[ ✅ ]: Virtual environment already exists. Skipping creation..."
    echo $UI_SEP
    echo ""
fi

echo $UI_SEP
echo "UPGRADING PIP..."
echo $UI_SEP
echo "[ ⬆️ ]:" Upgrading pip...
echo ""
pip install --upgrade pip
echo $UI_SEP
echo ""

echo $UI_SEP
echo "ACTIVATING VIRTUAL ENVIRONMENT"
echo $UI_SEP
echo "[ ✅ ]: Activating virtual environment..."
source venv/bin/activate
echo $UI_SEP
echo ""

echo $UI_SEP
echo "DEPENDENCIES"
echo $UI_SEP
echo "[ 📦 ]: Installing dependencies using pip..."
echo ""
pip install -r requirements.txt
echo $UI_SEP
echo ""

echo $UI_SEP
echo "YOU'RE ALL SET"
echo $UI_SEP
echo "[ ✅ ]: Environment is ready and dependencies are installed!"
echo $UI_SEP
echo ""