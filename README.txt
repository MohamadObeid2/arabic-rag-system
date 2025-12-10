# Move installers folder
Move installers folder to C:\

# Install the following packages:
1 Python
2 Vscode
3 Docker
4 rustup
5 WSL
6 ollama
7 visualstudio

# Install C++
cd C:\installers\packages\visualstudio\offline
C:\installers\packages\visualstudio\vs_community.exe --noWeb

# Source
cd <root-project>
python -m venv .venv
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
.venv\Scripts\activate

# install python libs
## Options:
    1. unzip .venv folder and mv to project root folder
    2. pip install --no-index --find-links=C:\installers\libraries -r requirements.txt

# Transfer .ollama folder to:
C:\Users\<Username>\.ollama\models\

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
./run.ps1 -service vanilla
