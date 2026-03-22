$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$lockedDir = Join-Path $scriptDir "locked"
$unlockedDir = Join-Path $scriptDir "unlocked"
$password = "llam0102"
$qpdfCmd = "qpdf"
$pollDelayMs = 1500

if (-not (Test-Path -LiteralPath $lockedDir -PathType Container)) {
    throw "Locked directory not found: $lockedDir"
}

if (-not (Test-Path -LiteralPath $unlockedDir -PathType Container)) {
    New-Item -ItemType Directory -Path $unlockedDir | Out-Null
}

if (-not (Get-Command $qpdfCmd -ErrorAction SilentlyContinue)) {
    throw "qpdf was not found in PATH. Add qpdf to PATH or run this script from a shell where qpdf is available."
}

function Get-UnlockedPath {
    param(
        [Parameter(Mandatory = $true)]
        [string] $InputPath
    )

    $baseName = [System.IO.Path]::GetFileNameWithoutExtension($InputPath)
    $extension = [System.IO.Path]::GetExtension($InputPath)
    return Join-Path $unlockedDir ("{0}_unlocked{1}" -f $baseName, $extension)
}

function Wait-FileReady {
    param(
        [Parameter(Mandatory = $true)]
        [string] $Path
    )

    for ($i = 0; $i -lt 20; $i++) {
        try {
            $stream = [System.IO.File]::Open($Path, "Open", "Read", "None")
            $stream.Close()
            return $true
        }
        catch {
            Start-Sleep -Milliseconds $pollDelayMs
        }
    }

    return $false
}

function Unlock-Pdf {
    param(
        [Parameter(Mandatory = $true)]
        [string] $InputPath
    )

    if (-not (Test-Path -LiteralPath $InputPath -PathType Leaf)) {
        Write-Warning "Skipped missing file: $InputPath"
        return
    }

    if ([System.IO.Path]::GetExtension($InputPath).ToLowerInvariant() -ne ".pdf") {
        Write-Host "Skipped non-PDF file: $InputPath"
        return
    }

    $outputPath = Get-UnlockedPath -InputPath $InputPath

    if (Test-Path -LiteralPath $outputPath -PathType Leaf) {
        Write-Host "Skipped existing output: $outputPath"
        return
    }

    if (-not (Wait-FileReady -Path $InputPath)) {
        Write-Warning "Timed out waiting for file to finish writing: $InputPath"
        return
    }

    Write-Host "Decrypting: $InputPath"
    & $qpdfCmd --password=$password --decrypt $InputPath $outputPath

    if ($LASTEXITCODE -ne 0) {
        if (Test-Path -LiteralPath $outputPath) {
            Remove-Item -LiteralPath $outputPath -Force
        }
        throw "qpdf decrypt failed for: $InputPath"
    }

    $status = & $qpdfCmd --show-encryption $outputPath
    if ($LASTEXITCODE -ne 0 -or ($status -notmatch "File is not encrypted")) {
        if (Test-Path -LiteralPath $outputPath) {
            Remove-Item -LiteralPath $outputPath -Force
        }
        throw "Decryption verification failed for: $outputPath"
    }

    Write-Host "Unlocked OK: $outputPath"
}

Get-ChildItem -LiteralPath $lockedDir -File -Filter *.pdf | Sort-Object Name | ForEach-Object {
    Unlock-Pdf -InputPath $_.FullName
}

$watcher = New-Object System.IO.FileSystemWatcher
$watcher.Path = $lockedDir
$watcher.Filter = "*.pdf"
$watcher.IncludeSubdirectories = $false
$watcher.NotifyFilter = [System.IO.NotifyFilters]'FileName, LastWrite, Size, CreationTime'
$watcher.EnableRaisingEvents = $true

$action = {
    try {
        Unlock-Pdf -InputPath $Event.SourceEventArgs.FullPath
    }
    catch {
        Write-Error $_
    }
}

$createdRegistration = Register-ObjectEvent -InputObject $watcher -EventName Created -Action $action
$renamedRegistration = Register-ObjectEvent -InputObject $watcher -EventName Renamed -Action $action

Write-Host "Watching for new PDFs in $lockedDir"
Write-Host "Decrypted files will be written to $unlockedDir"
Write-Host "Press Ctrl+C to stop."

try {
    while ($true) {
        Wait-Event -Timeout 5 | Out-Null
    }
}
finally {
    Unregister-Event -SourceIdentifier $createdRegistration.Name
    Unregister-Event -SourceIdentifier $renamedRegistration.Name
    $watcher.Dispose()
}
