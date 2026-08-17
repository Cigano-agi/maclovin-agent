# Script de configuracao do Maclovin no Windows Startup
$ErrorActionPreference = "Stop"

$ProjectDir = (Get-Item $PSScriptRoot).Parent.FullName
$VenvPythonW = Join-Path $ProjectDir ".venv\Scripts\pythonw.exe"
$VenvPython = Join-Path $ProjectDir ".venv\Scripts\python.exe"

if (Test-Path $VenvPythonW) {
    $PythonExe = $VenvPythonW
} elseif (Test-Path $VenvPython) {
    $PythonExe = $VenvPython
} else {
    Write-Host "[WARN] Ambiente virtual .venv nao encontrado. Usando python global..." -ForegroundColor Yellow
    $PythonExe = (Get-Command pythonw -ErrorAction SilentlyContinue).Source
    if (-not $PythonExe) {
        $PythonExe = (Get-Command python -ErrorAction SilentlyContinue).Source
    }
    if (-not $PythonExe) {
        Write-Error "Python nao encontrado. Execute 'uv sync' antes de continuar."
    }
}

$StartupFolder = [Environment]::GetFolderPath([Environment+SpecialFolder]::Startup)
$ShortcutPath = Join-Path $StartupFolder "MaclovinIntelligence.lnk"

Write-Host "[INFO] Configurando inicializacao automatica no Windows Startup..." -ForegroundColor Cyan
Write-Host " Pasta: $StartupFolder"
Write-Host " Alvo: $PythonExe"
Write-Host " Args: -m maclovin startup"
Write-Host " Dir:  $ProjectDir"

$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut($ShortcutPath)
$Shortcut.TargetPath = $PythonExe
$Shortcut.Arguments = "-m maclovin startup"
$Shortcut.WorkingDirectory = $ProjectDir
$Shortcut.Description = "Maclovin Intelligence Platform"
$Shortcut.Save()

Write-Host "[SUCESSO] Atalho de inicializacao criado em: $ShortcutPath" -ForegroundColor Green
Write-Host "[PRONTO] O Maclovin sera executado e abrira o painel no navegador automaticamente sempre que o PC ligar!" -ForegroundColor Green
