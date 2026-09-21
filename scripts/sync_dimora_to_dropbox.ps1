# DiMORA JSON -> Dropbox sync helper for Windows work_pc.
# Copies the latest exported JSON to a Dropbox folder. It does not upload to GitHub.
# Configure $DropboxTarget once, then run this script from Task Scheduler.

[CmdletBinding()]
param(
    [string]$Source = "$env:USERPROFILE\\Downloads\\dimora-favorite-programs.json",
    [string]$DropboxTarget = "$env:USERPROFILE\\Dropbox\\dimora\\dimora-favorite-programs.json"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

if (-not (Test-Path -LiteralPath $Source -PathType Leaf)) {
    throw "DiMORA export not found: $Source"
}

$targetDir = Split-Path -Parent $DropboxTarget
if (-not (Test-Path -LiteralPath $targetDir -PathType Container)) {
    New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
}

# Validate JSON before replacing the synced copy.
$json = Get-Content -LiteralPath $Source -Raw -Encoding UTF8 | ConvertFrom-Json
if ($null -eq $json) {
    throw "DiMORA JSON is empty or invalid: $Source"
}

$sourceInfo = Get-Item -LiteralPath $Source
$targetInfo = if (Test-Path -LiteralPath $DropboxTarget -PathType Leaf) { Get-Item -LiteralPath $DropboxTarget } else { $null }

# Avoid unnecessary writes when the source has not changed.
if ($null -ne $targetInfo -and $targetInfo.Length -eq $sourceInfo.Length) {
    $sourceHash = (Get-FileHash -LiteralPath $Source -Algorithm SHA256).Hash
    $targetHash = (Get-FileHash -LiteralPath $DropboxTarget -Algorithm SHA256).Hash
    if ($sourceHash -eq $targetHash) {
        Write-Output "UNCHANGED $Source -> $DropboxTarget"
        exit 0
    }
}

Copy-Item -LiteralPath $Source -Destination $DropboxTarget -Force
Write-Output "SYNCED $Source -> $DropboxTarget"
