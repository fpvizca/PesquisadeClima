@echo off
REM ============================================
REM Pesquisa de Clima Vizca - Inicializacao local
REM ============================================
setlocal

cd /d "%~dp0"

if not exist ".env" (
    if exist ".env.example" (
        copy ".env.example" ".env" >nul
        echo Arquivo .env criado a partir de .env.example
        echo IMPORTANTE: defina o SECRET_KEY antes de usar em producao.
        echo.
    )
)

if not exist "venv\Scripts\python.exe" (
    echo Criando ambiente virtual...
    python -m venv venv
    venv\Scripts\python.exe -m pip install --upgrade pip
    venv\Scripts\python.exe -m pip install -r requirements.txt
)

echo Aplicando migracoes no banco...
venv\Scripts\python.exe migrar.py
if errorlevel 1 (
    echo.
    echo FALHA ao aplicar migracoes. Corrija e tente novamente.
    pause
    exit /b 1
)

echo.
echo Iniciando Pesquisa de Clima...
echo Acesse: http://localhost:5005
echo.
venv\Scripts\python.exe app.py
pause
