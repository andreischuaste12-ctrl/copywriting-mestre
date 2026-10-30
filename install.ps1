<#
.SYNOPSIS
  Instalador da skill copywriter-mestre (Windows, PowerShell 5.1 ou superior).

.EXAMPLE
  .\install.ps1                      # instala nas pastas padrão do seu usuário
  .\install.ps1 -Dest "C:\pasta"     # instala só nessa pasta (aceita vários valores)
  .\install.ps1 -Project             # instala no diretório atual (somente este projeto)
  .\install.ps1 -Uninstall           # remove a skill dos mesmos destinos
  .\install.ps1 -DryRun              # mostra o que seria feito, sem alterar nada

.NOTES
  Se o PowerShell bloquear a execução de scripts, rode:
  powershell -ExecutionPolicy Bypass -File .\install.ps1
#>
[CmdletBinding()]
param(
  [string[]]$Dest,
  [switch]$Project,
  [switch]$Uninstall,
  [switch]$DryRun
)

$ErrorActionPreference = 'Stop'
$SkillName  = 'copywriter-mestre'
$ZipUrl     = 'https://github.com/andreischuaste12-ctrl/copywriting-mestre/archive/refs/heads/main.zip'
# Pastas de skills lidas por assistentes de IA compatíveis com o formato SKILL.md.
$DefaultSubdirs = @('.claude\skills', '.agents\skills')

if (-not $Dest -or $Dest.Count -eq 0) {
  $base = if ($Project) { (Get-Location).Path } else { $HOME }
  $Dest = $DefaultSubdirs | ForEach-Object { Join-Path $base $_ }
}

function Remove-SkillDir([string]$Target) {
  if ((Split-Path $Target -Leaf) -ne $SkillName) { throw "Recusado: caminho inesperado: $Target" }
  $md = Join-Path $Target 'SKILL.md'
  if (-not (Test-Path $md) -or -not (Select-String -Path $md -Pattern "^name: $SkillName\s*$" -Quiet)) {
    throw "Recusado: $Target existe, mas não parece ser esta skill. Remova ou mova manualmente."
  }
  if ($DryRun) { Write-Host "[dry-run] remover $Target" } else { Remove-Item -LiteralPath $Target -Recurse -Force }
}

if ($Uninstall) {
  foreach ($d in $Dest) {
    $t = Join-Path $d $SkillName
    if (Test-Path $t) { Remove-SkillDir $t; Write-Host "Removida: $t" } else { Write-Host "Não encontrada: $t" }
  }
  return
}

# Localiza o código-fonte: ao lado do script, ou baixa o repositório.
$src = $null
$tmp = $null
if ($PSScriptRoot -and (Test-Path (Join-Path $PSScriptRoot "skills\$SkillName\SKILL.md"))) {
  $src = Join-Path $PSScriptRoot "skills\$SkillName"
} else {
  $tmp = Join-Path ([System.IO.Path]::GetTempPath()) ("$SkillName-" + [guid]::NewGuid())
  New-Item -ItemType Directory -Path $tmp | Out-Null
  $zip = Join-Path $tmp 'repo.zip'
  Write-Host 'Baixando a skill...'
  Invoke-WebRequest -Uri $ZipUrl -OutFile $zip -UseBasicParsing
  Expand-Archive -Path $zip -DestinationPath $tmp -Force
  $found = Get-ChildItem -Path $tmp -Directory -Recurse | Where-Object { $_.FullName -like "*\skills\$SkillName" } | Select-Object -First 1
  if (-not $found -or -not (Test-Path (Join-Path $found.FullName 'SKILL.md'))) { throw 'Skill não encontrada no download.' }
  $src = $found.FullName
}

try {
  foreach ($d in $Dest) {
    $t = Join-Path $d $SkillName
    if ($DryRun) { Write-Host "[dry-run] copiar $src -> $t"; continue }
    New-Item -ItemType Directory -Path $d -Force | Out-Null
    if (Test-Path $t) { Remove-SkillDir $t }
    Copy-Item -LiteralPath $src -Destination $t -Recurse
    if (-not (Test-Path (Join-Path $t 'SKILL.md'))) { throw "Falha ao instalar em $t" }
    Write-Host "Instalada: $t"
  }
} finally {
  if ($tmp -and (Test-Path $tmp)) { Remove-Item -LiteralPath $tmp -Recurse -Force }
}

Write-Host ''
Write-Host 'Pronto. Reinicie seu assistente de IA (ou abra uma nova sessão) e peça, por exemplo:'
Write-Host '  "Crie headlines para o meu produto"'
