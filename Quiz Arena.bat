@echo off
setlocal
cd /d "%~dp0"

rem Abre o Quiz Arena Desktop (Tkinter) sem janela de console.
rem Requer Python 3.11 ou superior instalado com o Tkinter.

set "PYW="
where pythonw >nul 2>nul && set "PYW=pythonw"
if not defined PYW (
  where py >nul 2>nul && set "PYW=py -w"
)

if not defined PYW (
  echo.
  echo Python nao encontrado.
  echo Instale o Python 3.11 ou superior em https://www.python.org/downloads/
  echo Durante a instalacao, marque a opcao "Add Python to PATH".
  echo.
  pause
  exit /b 1
)

start "" %PYW% "desktop\app.py"
exit /b 0
