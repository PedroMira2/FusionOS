# ==============================================================================
# FusionOS - Baixar ISO Oficial do GitHub Actions
# ==============================================================================
param (
    [string]$DestinationDir = "$env:USERPROFILE\Downloads"
)

$repo = "PedroMira2/FusionOS"
Write-Host "Verificando ultima ISO gerada no repositorio $repo..." -ForegroundColor Cyan

# Obter token do git se disponivel
$token = ""
try {
    $proc = Start-Process -FilePath "git" -ArgumentList "credential fill" -PassThru -NoNewWindow -RedirectStandardInput "cred.txt" -RedirectStandardOutput "out.txt"
} catch {}

# Buscar ultimo artifact
$headers = @{"User-Agent"="FusionOS-CLI"}
try {
    $creds = cmd.exe /c "@echo protocol=https& @echo host=github.com& @echo.| C:\Users\pedro\AppData\Local\Programs\MinGit\cmd\git.exe credential fill" 2>$null
    foreach ($line in $creds) {
        if ($line -like "password=*") {
            $token = $line.Substring(9)
            $headers["Authorization"] = "Bearer $token"
        }
    }
} catch {}

$runs = Invoke-RestMethod -Uri "https://api.github.com/repos/$repo/actions/artifacts" -Headers $headers
$artifact = $runs.artifacts | Where-Object { $_.name -eq "FusionOS-Live-x86_64" -and -not $_.expired } | Select-Object -First 1

if (-not $artifact) {
    Write-Host "Nenhum artefato FusionOS-Live-x86_64 ativo encontrado." -ForegroundColor Red
    exit 1
}

$sizeMb = [math]::Round($artifact.size_in_bytes / 1MB, 2)
Write-Host "ISO encontrada: $($artifact.name) ($sizeMb MB)" -ForegroundColor Green
Write-Host "Baixando para $DestinationDir..." -ForegroundColor Yellow

$zipPath = Join-Path $DestinationDir "FusionOS-Live-x86_64.zip"
Invoke-WebRequest -Uri $artifact.archive_download_url -Headers $headers -OutFile $zipPath

Write-Host "Download concluido! Extraindo imagem ISO..." -ForegroundColor Cyan
Expand-Archive -Path $zipPath -DestinationPath $DestinationDir -Force
Remove-Item $zipPath -Force

Write-Host "Sucesso! A ISO esta pronta em: $DestinationDir\FusionOS-Live-x86_64.iso" -ForegroundColor Green
