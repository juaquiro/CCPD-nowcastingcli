@echo off
REM sync_env.bat
REM Hace git pull y actualiza el entorno conda local con el lock descargado.
REM
REM EJECUTAR CON:
REM   scripts\sync_env.bat

setlocal

REM Activar codigos ANSI de color (Windows 10+)
for /f %%a in ('echo prompt $E ^| cmd') do set "ESC=%%a"
set "GREEN=%ESC%[32m"
set "RED=%ESC%[31m"
set "YELLOW=%ESC%[33m"
set "NC=%ESC%[0m"

set ENV_NAME=nowcastingcli
set LOCK_FILE=environment.lock.yml

echo %GREEN%[INFO]%NC% Iniciando sync_env...

if not exist ".git\config" (
    echo %RED%[ERROR]%NC% Ejecuta este script desde la raiz del repositorio.
    exit /b 1
)
echo %GREEN%[INFO]%NC% Repositorio Git encontrado.

git diff --quiet >nul 2>&1
if errorlevel 1 (
    echo %YELLOW%[WARN]%NC% Tienes cambios locales sin commitear.
    set /p RESP=Continuar con git pull de todas formas? [s/N]: 
    if /i not "%RESP%"=="s" exit /b 0
)

echo %GREEN%[INFO]%NC% Haciendo git pull...
git pull
if errorlevel 1 (
    echo %RED%[ERROR]%NC% Fallo en git pull.
    exit /b 1
)

if not exist "%LOCK_FILE%" (
    echo %RED%[ERROR]%NC% No se encuentra %LOCK_FILE% tras el pull.
    exit /b 1
)

conda env list | findstr /B "%ENV_NAME%" >nul 2>&1
if errorlevel 1 (
    echo %GREEN%[INFO]%NC% El entorno no existe localmente. Creandolo desde el lock...
    conda env create --file %LOCK_FILE%
) else (
    echo %GREEN%[INFO]%NC% Actualizando entorno existente...
    conda env update -n %ENV_NAME% --file %LOCK_FILE% --prune
)

if errorlevel 1 (
    echo %RED%[ERROR]%NC% Fallo al actualizar el entorno conda.
    exit /b 1
)

echo %GREEN%[INFO]%NC% Entorno sincronizado correctamente.
endlocal
