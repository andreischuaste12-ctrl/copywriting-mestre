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

function Get-CanonicalPath([string]$Path) {
  $full = if ([System.IO.Path]::IsPathRooted($Path)) { $Path } else { Join-Path (Get-Location).Path $Path }
  $root = [System.IO.Path]::GetPathRoot($full)
  $current = $root
  $relative = $full.Substring($root.Length)
  foreach ($part in ($relative -split '[\\/]+' | Where-Object { $_ })) {
    if ($part -eq '.') { continue }
    if ($part -eq '..') {
      $parent = [System.IO.Path]::GetDirectoryName($current)
      if ($parent) { $current = $parent }
      continue
    }
    $candidate = Join-Path $current $part
    if (Test-Path -LiteralPath $candidate) {
      $item = Get-Item -LiteralPath $candidate -Force
      if (($item.Attributes -band [System.IO.FileAttributes]::ReparsePoint) -ne 0) {
        throw "Recusado: o caminho contém link simbólico ou junction; use o caminho físico: $candidate"
      }
      $current = $item.FullName
    } else {
      $current = Join-Path $current $part
    }
  }
  return [System.IO.Path]::GetFullPath($current)
}

function Test-PathsOverlap([string]$First, [string]$Second) {
  $trimChars = [char[]]@(92, 47)
  $a = $First.TrimEnd($trimChars)
  $b = $Second.TrimEnd($trimChars)
  if ([string]::Equals($a, $b, [System.StringComparison]::OrdinalIgnoreCase)) { return $true }
  $separator = [System.IO.Path]::DirectorySeparatorChar
  return $a.StartsWith($b + $separator, [System.StringComparison]::OrdinalIgnoreCase) -or
    $b.StartsWith($a + $separator, [System.StringComparison]::OrdinalIgnoreCase)
}

function Test-SkillContents([string]$Target) {
  $md = Join-Path $Target 'SKILL.md'
  if (-not (Test-Path -LiteralPath $md -PathType Leaf)) { return $false }
  return [bool](Select-String -LiteralPath $md -Pattern "^name: $SkillName\s*$" -Quiet)
}

function Assert-SkillDir([string]$Target) {
  if ((Split-Path $Target -Leaf) -ne $SkillName) { throw "Recusado: caminho inesperado: $Target" }
  if (-not (Test-SkillContents $Target)) {
    throw "Recusado: $Target existe, mas não parece ser esta skill. Remova ou mova manualmente."
  }
}

function Remove-SkillDir([string]$Target) {
  Assert-SkillDir $Target
  if ($DryRun) { Write-Host "[dry-run] remover $Target" } else { Remove-Item -LiteralPath $Target -Recurse -Force }
}

$LocalSrc = $null
if ($PSScriptRoot -and (Test-Path (Join-Path $PSScriptRoot "skills\$SkillName\SKILL.md"))) {
  $LocalSrc = Get-CanonicalPath (Join-Path $PSScriptRoot "skills\$SkillName")
  Assert-SkillDir $LocalSrc
}

if ($Uninstall) {
  foreach ($d in $Dest) {
    $t = Join-Path $d $SkillName
    if (Test-Path -LiteralPath $t) {
      if ($LocalSrc) {
        $resolvedTarget = Get-CanonicalPath $t
        if (Test-PathsOverlap $LocalSrc $resolvedTarget) {
          throw "Recusado: o destino coincide ou se sobrepõe à pasta de origem: $t"
        }
      }
      Remove-SkillDir $t
      Write-Host "Removida: $t"
    } else { Write-Host "Não encontrada: $t" }
  }
  return
}

# Localiza o código-fonte: ao lado do script, ou baixa o repositório.
$src = $null
$tmp = $null
if ($LocalSrc) {
  $src = $LocalSrc
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
$src = Get-CanonicalPath $src
Assert-SkillDir $src

try {
  foreach ($d in $Dest) {
    $t = Join-Path $d $SkillName
    $resolvedTarget = Get-CanonicalPath $t
    if (Test-PathsOverlap $src $resolvedTarget) {
      throw "Recusado: o destino coincide ou se sobrepõe à pasta de origem: $t"
    }
    if (Test-Path -LiteralPath $t) { Assert-SkillDir $t }

    if ($DryRun) {
      Write-Host "[dry-run] prepararia e validaria uma cópia de $src"
      if (Test-Path -LiteralPath $t) { Write-Host "[dry-run] substituiria a instalação reconhecida em $t" }
      else { Write-Host "[dry-run] instalaria em $t" }
      continue
    }

    New-Item -ItemType Directory -Path $d -Force | Out-Null
    $stage = Join-Path $d (".$SkillName.stage-" + [guid]::NewGuid().ToString('N'))
    $backup = $null
    try {
      New-Item -ItemType Directory -Path $stage | Out-Null
      Get-ChildItem -LiteralPath $src -Force | ForEach-Object {
        Copy-Item -LiteralPath $_.FullName -Destination $stage -Recurse -Force
      }
      if (-not (Test-SkillContents $stage)) { throw 'A cópia preparada não passou na validação.' }

      if (Test-Path -LiteralPath $t) {
        $backup = Join-Path $d (".$SkillName.backup-" + [guid]::NewGuid().ToString('N'))
        New-Item -ItemType Directory -Path $backup | Out-Null
        Move-Item -LiteralPath $t -Destination (Join-Path $backup 'previous')
      }
      try {
        Move-Item -LiteralPath $stage -Destination $t
      } catch {
        if ($backup -and (Test-Path -LiteralPath (Join-Path $backup 'previous')) -and -not (Test-Path -LiteralPath $t)) {
          Move-Item -LiteralPath (Join-Path $backup 'previous') -Destination $t
        }
        throw
      }
      if ($backup -and (Test-Path -LiteralPath $backup)) {
        try { Remove-Item -LiteralPath $backup -Recurse -Force }
        catch { Write-Warning "Instalação concluída; não foi possível remover o backup $backup" }
      }
      Write-Host "Instalada: $t"
    } finally {
      if (Test-Path -LiteralPath $stage) { Remove-Item -LiteralPath $stage -Recurse -Force }
      if ($backup -and (Test-Path -LiteralPath $backup) -and -not (Test-Path -LiteralPath (Join-Path $backup 'previous'))) {
        Remove-Item -LiteralPath $backup -Recurse -Force
      }
    }
  }
} finally {
  if ($tmp -and (Test-Path $tmp)) { Remove-Item -LiteralPath $tmp -Recurse -Force }
}

Write-Host ''
Write-Host 'Pronto. Reinicie seu assistente de IA (ou abra uma nova sessão) e peça, por exemplo:'
Write-Host '  "Crie headlines para o meu produto"'
