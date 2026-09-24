@echo off
title Enviando FusionOS para o GitHub...
echo ======================================================
echo    Enviando FusionOS para https://github.com/PedroMira2/FusionOS
echo ======================================================
echo.
set "PATH=C:\Users\pedro\AppData\Local\Programs\MinGit\cmd;%PATH%"
cd /d "C:\Users\pedro\Desktop\HEAK"
git add -A
git commit -m "Update FusionOS configs and scripts"
git push -u origin main
echo.
if %ERRORLEVEL% EQU 0 (
    echo [SUCESSO] Todos os arquivos do FusionOS estao no seu GitHub!
) else (
    echo [AVISO] Se solicitou senha, o GitHub utiliza um Personal Access Token (PAT).
)
echo.
pause

