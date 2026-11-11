# PowerShell script for initializing skill output directory and INFO.md
# Usage: .\init_skill_output.ps1 -SkillName <skill_name> -ExecutedBy <executed_by> -Prompt <prompt>

param (
    [Parameter(Mandatory=$true)][string]$SkillName,
    [Parameter(Mandatory=$true)][string]$ExecutedBy,
    [Parameter(Mandatory=$true)][string]$Prompt
)

$dateStr = Get-Date -Format "MM-dd-yyyy"
$outputBaseDir = "output-skills/$SkillName"

$counter = 1
do {
    $counterStr = "{0:D2}" -f $counter
    $targetDir = "$outputBaseDir/${dateStr}_$counterStr"
    $counter++
} while (Test-Path -Path $targetDir)

New-Item -ItemType Directory -Path $targetDir -Force | Out-Null

$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss zzz"
$infoContent = @"
# Execution Information

- **Skill**: $SkillName
- **Executed By**: $ExecutedBy
- **Date & Time**: $timestamp
- **Prompt**:
$Prompt
"@

Set-Content -Path "$targetDir/INFO.md" -Value $infoContent -Encoding UTF8

Write-Output $targetDir
