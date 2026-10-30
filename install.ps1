<#
.SYNOPSIS
  Installer for the skill copywriter-master (Windows, PowerShell 5.1 or later).

.EXAMPLE
  .\install.ps1                      # installs to the default user directories
  .\install.ps1 -Dest "C:\path"     # installs only to this directory (accepts multiple values)
  .\install.ps1 -Project             # installs in the current directory (this project only)
  .\install.ps1 -Uninstall           # removes the skill from the same destinations
  .\install.ps1 -DryRun              # shows what would happen without making changes

.NOTES
  If PowerShell blocks script execution, run:
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
$SkillName  = 'copywriter-master'
$ZipUrl     = 'https://github.com/andreischuaste12-ctrl/copywriting-mestre/archive/refs/heads/main.zip'
# Skill directories read by AI assistants that support the SKILL.md format.
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
        throw "Refused: path contains a symbolic link or junction; use the physical path: $candidate"
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
  if ((Split-Path $Target -Leaf) -ne $SkillName) { throw "Refused: unexpected path: $Target" }
  if (-not (Test-SkillContents $Target)) {
    throw "Refused: $Target exists but does not appear to be this skill. Remove or move it manually."
  }
}

function Remove-SkillDir([string]$Target) {
  Assert-SkillDir $Target
  if ($DryRun) { Write-Host "[dry-run] remove $Target" } else { Remove-Item -LiteralPath $Target -Recurse -Force }
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
          throw "Refused: destination matches or overlaps the source directory: $t"
        }
      }
      Remove-SkillDir $t
      Write-Host "Removed: $t"
    } else { Write-Host "Not found: $t" }
  }
  return
}

# Locate source beside this script, or download the repository.
$src = $null
$tmp = $null
if ($LocalSrc) {
  $src = $LocalSrc
} else {
  $tmp = Join-Path ([System.IO.Path]::GetTempPath()) ("$SkillName-" + [guid]::NewGuid())
  New-Item -ItemType Directory -Path $tmp | Out-Null
  $zip = Join-Path $tmp 'repo.zip'
  Write-Host 'Downloading the skill...'
  Invoke-WebRequest -Uri $ZipUrl -OutFile $zip -UseBasicParsing
  Expand-Archive -Path $zip -DestinationPath $tmp -Force
  $found = Get-ChildItem -Path $tmp -Directory -Recurse | Where-Object { $_.FullName -like "*\skills\$SkillName" } | Select-Object -First 1
  if (-not $found -or -not (Test-Path (Join-Path $found.FullName 'SKILL.md'))) { throw 'Skill not found in the download.' }
  $src = $found.FullName
}
$src = Get-CanonicalPath $src
Assert-SkillDir $src

try {
  foreach ($d in $Dest) {
    $t = Join-Path $d $SkillName
    $resolvedTarget = Get-CanonicalPath $t
    if (Test-PathsOverlap $src $resolvedTarget) {
      throw "Refused: destination matches or overlaps the source directory: $t"
    }
    if (Test-Path -LiteralPath $t) { Assert-SkillDir $t }

    if ($DryRun) {
      Write-Host "[dry-run] would stage and validate a copy of $src"
      if (Test-Path -LiteralPath $t) { Write-Host "[dry-run] would replace the recognized installation at $t" }
      else { Write-Host "[dry-run] would install to $t" }
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
      if (-not (Test-SkillContents $stage)) { throw 'The staged copy did not pass validation.' }

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
        catch { Write-Warning "Installation completed; could not remove backup $backup" }
      }
      Write-Host "Installed: $t"
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
Write-Host 'Done. Restart your AI assistant (or open a new session) and try a request such as:'
Write-Host '  "Write headlines for my product"'
