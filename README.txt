# Move installers folder
Move installers folder from flash drive to C:\

# Open cmd
Open cmd from installers folder

# Install the following packages which exist in packages folder:
1 Python: C:\installers\packages\python\python-3.12.3-amd64.exe
2 Vscode: C:\installers\packages\vscode\VSCodeUserSetup-x64-1.106.3.exe
3 Docker: C:\installers\packages\docker\Docker Desktop Installer.exe
4 rustup: C:\installers\packages\rustup\rustup-init.exe
5 WSL: C:\installers\packages\wsl\wsl.2.6.2.0.x64.msi
6 Ollama: C:\installers\packages\ollama\OllamaSetup.exe

# Install visual studio and C++
C:\installers\packages\visualstudio\vs_community.exe --noWeb

# Source
cd arabic-rag-system
python -m venv .venv
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
.venv\Scripts\activate

# install python libs
## Options:
    1. unzip .venv folder
    2. using pip installer:
        2.1. pip install --no-index --find-links=C:\installers\libraries --upgrade pip setuptools wheel
        2.2. pip install --no-index --find-links=C:\installers\libraries -r requirements.txt

# Transfer .ollama folder from installers to:
C:\Users\<Username>\

# Verirfy ollama model
ollama list

# Load docker images: first run docker desktop
cd C:\installers\docker-images
docker load -i mongo.tar
docker load -i etcd.tar
docker load -i minio.tar
docker load -i milvus.tar

# Run docker containers
docker compose up -d

# Run app
## Options (but lets run vanilla app first):
    1. Vanilla: C:\installers\arabic-rag-system\run.ps1 -service vanilla
    2. Langchain: C:\installers\arabic-rag-system\run.ps1 -service langchain