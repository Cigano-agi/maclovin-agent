# Script de remocao do Maclovin do Windows Startup
$ErrorActionPreference = "Stop"

$StartupFolder = [Environment]::GetFolderPath([Environment+SpecialFolder]::Startup)
$Shortcuts = @(
    (Join-Path $StartupFolder "MaclovinIntelligence.lnk"),
    (Join-Path $StartupFolder "MaclovinDailyAgent.lnk")
)

foreach ($sc in $Shortcuts) {
    if (Test-Path $sc) {
        Remove-Item -Path $sc -Force
        Write-Host "[REMOVIDO] $sc" -ForegroundColor Yellow
    }
}

Write-Host "[SUCESSO] Inicializacao automatica desativada." -ForegroundColor Green
