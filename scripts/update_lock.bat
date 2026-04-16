@echo off
REM update_lock.bat
REM Regenera environment.lock.yml y sube los cambios a Git.
REM
REM EJECUTAR CON:
REM   scripts\update_lock.bat
REM   scripts\update_lock.bat "mensaje de commit personalizado"

setlocal

REM Activar codigos ANSI de color (Windows 10+)
for /f %%a in ('echo prompt $E ^| cmd') do set "ESC=%%a"
set "GREEN=%ESC%[32m"
set "RED=%ESC%[31m"
set "YELLOW=%ESC%[33m"
set "NC=%ESC%[0m"

set ENV_NAME=nowcastingcli
set LOCK_FILE=environment.lock.yml
if "%~1"=="" (
    set COMMIT_MSG=deps: actualizar environment.lock.yml
) else (
    set COMMIT_MSG=%~1
)

echo %GREEN%[INFO]%NC% Iniciando update_lock...

if not exist ".git\config" (
    echo %RED%[ERROR]%NC% Ejecuta este script desde la raiz del repositorio.
    exit /b 1
)
echo %GREEN%[INFO]%NC% Repositorio Git encontrado.

conda env list | findstr /B "%ENV_NAME%" >nul 2>&1
if errorlevel 1 (
    echo %RED%[ERROR]%NC% El entorno conda no existe. Comprueba ENV_NAME en el script.
    exit /b 1
)
echo %GREEN%[INFO]%NC% Entorno conda encontrado.

REM Exportar en proceso hijo separado para evitar que conda mate este bat
echo %GREEN%[INFO]%NC% Exportando lock...
cmd /c "conda env export -n %ENV_NAME% > %LOCK_FILE%"

if not exist "%LOCK_FILE%" (
    echo %RED%[ERROR]%NC% Fallo al exportar: no se ha creado %LOCK_FILE%.
    exit /b 1
)
echo %GREEN%[INFO]%NC% Lock generado: %LOCK_FILE%

echo %GREEN%[INFO]%NC% Anadiendo %LOCK_FILE% a Git...
git add %LOCK_FILE%

git diff --cached --quiet %LOCK_FILE%
if %ERRORLEVEL%==0 (
    echo %YELLOW%[WARN]%NC% El lock no ha cambiado. Nada que subir.
    exit /b 0
)

echo %GREEN%[INFO]%NC% Commiteando...
git commit -m "%COMMIT_MSG%"
if errorlevel 1 (
    echo %RED%[ERROR]%NC% Fallo en git commit.
    exit /b 1
)

echo %GREEN%[INFO]%NC% Subiendo a remoto...
git push
if errorlevel 1 (
    echo %RED%[ERROR]%NC% Fallo en git push.
    exit /b 1
)

echo %GREEN%[INFO]%NC% Lock actualizado y subido correctamente.
endlocal
