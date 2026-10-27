# NewsMind deploy to the Ubuntu debug host, port 8007.
# Run from the repo root:
#   pwsh -File .\deploy.ps1
#   powershell -File .\deploy.ps1
#
# Defaults:
#   root@47.97.245.103:/www/wwwroot/NewsMind8007   port 8007

[CmdletBinding()]
param(
    [switch]$DryRun,
    [switch]$SkipRestart,
    [switch]$SkipBuild
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $Root

function Write-Info {
    param([string]$Message)
    Write-Host ('[info] ' + $Message)
}

function Raise-DeployError {
    param([string]$Message)
    throw ('[error] ' + $Message)
}

function Get-CleanText {
    param([string]$Text)
    if ([string]::IsNullOrEmpty($Text)) { return "" }
    return $Text.Replace("`r", "").Replace("`n", "").Trim()
}

function Quote-BashSingle {
    param([string]$Value)
    $clean = Get-CleanText $Value
    return ("'" + $clean.Replace("'", "'\''") + "'")
}

function Read-DeployEnv {
    param([string]$Path)
    if (-not (Test-Path $Path)) { return }
    Get-Content -Path $Path -Encoding UTF8 | ForEach-Object {
        $line = Get-CleanText $_
        if (-not $line -or $line.StartsWith("#") -or ($line -notmatch "=")) { return }
        $key, $val = $line.Split("=", 2)
        $key = Get-CleanText $key
        $val = (Get-CleanText $val).Trim("'").Trim('"')
        Set-Item -Path "Env:$key" -Value $val
    }
}

Read-DeployEnv (Join-Path $Root "deploy.env")

$HostName = Get-CleanText $(if ($env:DEPLOY_HOST) { $env:DEPLOY_HOST } else { "47.97.245.103" })
$UserName = Get-CleanText $(if ($env:DEPLOY_USER) { $env:DEPLOY_USER } else { "root" })
$RemotePath = Get-CleanText $(if ($env:DEPLOY_PATH) { $env:DEPLOY_PATH } else { "/www/wwwroot/NewsMind8007" })
$SshPort = Get-CleanText $(if ($env:DEPLOY_SSH_PORT) { $env:DEPLOY_SSH_PORT } else { "22" })
$AppPort = Get-CleanText $(if ($env:APP_PORT) { $env:APP_PORT } else { "8007" })
$Password = Get-CleanText $(if ($env:DEPLOY_PASS) { $env:DEPLOY_PASS } else { "" })
$Remote = "${UserName}@${HostName}"
$SiteUrl = "http://${HostName}:${AppPort}/"

Write-Info ("target  {0}:{1}" -f $Remote, $SshPort)
Write-Info ("path    {0}" -f $RemotePath)
Write-Info ("url     {0}" -f $SiteUrl)

foreach ($cmd in @("ssh", "scp", "tar")) {
    if (-not (Get-Command $cmd -ErrorAction SilentlyContinue)) {
        Raise-DeployError ("missing command {0}" -f $cmd)
    }
}

$script:AskPassFile = $null
$script:UsePassword = $false
$stage = $null
$tarball = $null

function Clear-AskPass {
    if ($script:AskPassFile -and (Test-Path $script:AskPassFile)) {
        Remove-Item -Force $script:AskPassFile -ErrorAction SilentlyContinue
    }
    Remove-Item Env:SSH_ASKPASS -ErrorAction SilentlyContinue
    Remove-Item Env:SSH_ASKPASS_REQUIRE -ErrorAction SilentlyContinue
}

function Enable-PasswordAuth {
    if (-not $Password) {
        Raise-DeployError "SSH key failed and deploy.env has no DEPLOY_PASS"
    }
    $ask = Join-Path $env:TEMP ("newsmind-askpass-{0}.cmd" -f [guid]::NewGuid().ToString("n"))
    $esc = $Password.Replace("%", "%%")
    Set-Content -Path $ask -Value "@echo off`r`necho $esc" -Encoding ASCII -NoNewline
    $script:AskPassFile = $ask
    $env:SSH_ASKPASS = $ask
    $env:SSH_ASKPASS_REQUIRE = "force"
    $env:DISPLAY = "localhost:0"
    $script:UsePassword = $true
}

function Get-SshArgs {
    $opts = @(
        "-p", $SshPort,
        "-o", "StrictHostKeyChecking=accept-new",
        "-o", "ServerAliveInterval=30",
        "-o", "ConnectTimeout=12"
    )
    if ($script:UsePassword) {
        $opts += @(
            "-o", "PreferredAuthentications=password",
            "-o", "PubkeyAuthentication=no",
            "-o", "NumberOfPasswordPrompts=1"
        )
    }
    return $opts
}

function Invoke-Remote {
    param(
        [Parameter(Mandatory = $true)][string]$RemoteCommand,
        [switch]$IgnoreFailure
    )
    $cmd = Get-CleanText $RemoteCommand
    $sshArgs = (Get-SshArgs) + @("-o", "RequestTTY=no", $Remote, "--", $cmd)
    if ($IgnoreFailure) {
        $prev = $ErrorActionPreference
        $ErrorActionPreference = "Continue"
        & ssh @sshArgs 1>$null 2>$null
        $ErrorActionPreference = $prev
    } else {
        & ssh @sshArgs
    }
    if (-not $IgnoreFailure -and $LASTEXITCODE -ne 0) {
        Raise-DeployError ("remote command failed (exit {0}): {1}" -f $LASTEXITCODE, $cmd)
    }
    return $LASTEXITCODE
}

function Test-SshKeyLogin {
    $probe = @(
        "-p", $SshPort,
        "-o", "BatchMode=yes",
        "-o", "ConnectTimeout=8",
        "-o", "StrictHostKeyChecking=accept-new",
        $Remote, "true"
    )
    & ssh @probe 2>$null | Out-Null
    return ($LASTEXITCODE -eq 0)
}

try {
    if (-not $SkipBuild) {
        $frontend = Join-Path $Root "frontend"
        if (-not (Test-Path (Join-Path $frontend "package.json"))) {
            Raise-DeployError "missing frontend/package.json"
        }
        Push-Location $frontend
        try {
            if (-not (Test-Path (Join-Path $frontend "node_modules"))) {
                Write-Info "npm ci ..."
                & npm ci
                if ($LASTEXITCODE -ne 0) { Raise-DeployError "npm ci failed" }
            }
            Write-Info "npm run build ..."
            & npm run build
            if ($LASTEXITCODE -ne 0) { Raise-DeployError "frontend build failed" }
        } finally {
            Pop-Location
        }
    }

    $distIndex = Join-Path $Root "frontend\dist\index.html"
    if (-not (Test-Path $distIndex)) {
        Raise-DeployError "missing frontend/dist/index.html"
    }
    if (-not (Test-Path (Join-Path $Root "backend\app\main.py"))) {
        Raise-DeployError "missing backend/app/main.py"
    }
    if (-not (Test-Path (Join-Path $Root "start.sh"))) {
        Raise-DeployError "missing start.sh"
    }

    $stage = Join-Path $env:TEMP ("newsmind-stage-" + [guid]::NewGuid().ToString("n"))
    New-Item -ItemType Directory -Path $stage | Out-Null
    New-Item -ItemType Directory -Path (Join-Path $stage "backend") | Out-Null
    Copy-Item (Join-Path $Root "start.sh") (Join-Path $stage "start.sh")
    Copy-Item (Join-Path $Root "backend\requirements-prod.txt") (Join-Path $stage "backend\requirements-prod.txt")
    Copy-Item -Recurse -Force (Join-Path $Root "backend\app") (Join-Path $stage "backend\app")
    Copy-Item -Recurse -Force (Join-Path $Root "frontend\dist") (Join-Path $stage "frontend\dist")
    Get-ChildItem $stage -Recurse -Directory -Filter "__pycache__" | Remove-Item -Recurse -Force

    Write-Info "upload: start.sh, backend/app, requirements-prod.txt, frontend/dist"
    Write-Info "keep remote: backend/.venv, backend/newsmind.db, logs"

    if ($DryRun) {
        Write-Host ('[dry-run] stage: ' + $stage)
        Get-ChildItem $stage -Recurse -File | ForEach-Object {
            Write-Host ("  " + $_.FullName.Substring($stage.Length))
        }
        return
    }

    if (Test-SshKeyLogin) {
        Write-Info "SSH key login ok"
    } else {
        Enable-PasswordAuth
        Write-Info "using password login"
    }

    $tarball = Join-Path $env:TEMP ("newsmind-deploy-" + [guid]::NewGuid().ToString("n") + ".tgz")
    Write-Info "packing ..."
    & tar -czf $tarball -C $stage .
    if ($LASTEXITCODE -ne 0) { Raise-DeployError "tar failed" }

    $remoteTar = "/tmp/newsmind-deploy.tgz"
    Write-Info "uploading ..."
    $scpArgs = @(
        "-P", $SshPort,
        "-o", "StrictHostKeyChecking=accept-new",
        "-o", "ConnectTimeout=20"
    )
    if ($script:UsePassword) {
        $scpArgs += @(
            "-o", "PreferredAuthentications=password",
            "-o", "PubkeyAuthentication=no",
            "-o", "NumberOfPasswordPrompts=1"
        )
    }
    $scpArgs += @($tarball, "${Remote}:${remoteTar}")
    & scp @scpArgs
    if ($LASTEXITCODE -ne 0) { Raise-DeployError "scp failed" }

    Write-Info "extracting ..."
    $extract = @(
        ("mkdir -p {0}" -f (Quote-BashSingle $RemotePath))
        ("tar -xzf {0} -C {1}" -f (Quote-BashSingle $remoteTar), (Quote-BashSingle $RemotePath))
        ("rm -f {0}" -f (Quote-BashSingle $remoteTar))
        ("sed -i 's/\r$//' {0}" -f (Quote-BashSingle "$RemotePath/start.sh"))
        ("chmod +x {0}" -f (Quote-BashSingle "$RemotePath/start.sh"))
    ) -join " && "
    Invoke-Remote $extract

    if ($SkipRestart) {
        Write-Info ("uploaded to {0}, restart skipped" -f $RemotePath)
        return
    }

    Write-Info "installing deps and starting (first run can take a few minutes) ..."
    $startSh = Quote-BashSingle "$RemotePath/start.sh"
    $restart = ('bash {0} --stop >/dev/null 2>&1 || true; bash {0} --daemon' -f $startSh)
    Invoke-Remote $restart

    Write-Info ("opening firewall port {0} if ufw is present ..." -f $AppPort)
    Invoke-Remote ('command -v ufw >/dev/null 2>&1 && ufw allow {0}/tcp || true' -f $AppPort)

    Write-Info "waiting for health ..."
    $healthPy = "import urllib.request; urllib.request.urlopen('http://127.0.0.1:${AppPort}/health', timeout=5).read(80)"
    $healthCmd = ('python3 -c {0}' -f (Quote-BashSingle $healthPy))
    $healthy = $false
    for ($i = 0; $i -lt 30; $i++) {
        $code = Invoke-Remote -RemoteCommand $healthCmd -IgnoreFailure
        if ($code -eq 0) {
            $healthy = $true
            break
        }
        Start-Sleep -Seconds 2
    }

    if (-not $healthy) {
        Write-Host '[error] health check failed. recent log:'
        try {
            Invoke-Remote ('tail -n 80 {0} 2>/dev/null || echo no-log' -f (Quote-BashSingle "$RemotePath/logs/newsmind.log"))
        } catch {}
        Raise-DeployError ("site did not respond at {0}" -f $SiteUrl)
    }

    Write-Host ('[done] ' + $SiteUrl)
    try { Invoke-Remote ('bash {0} --status' -f (Quote-BashSingle "$RemotePath/start.sh")) } catch {}
}
finally {
    Clear-AskPass
    if ($stage -and (Test-Path $stage) -and -not $DryRun) {
        Remove-Item -Recurse -Force $stage -ErrorAction SilentlyContinue
    }
    if ($tarball -and (Test-Path $tarball)) {
        Remove-Item -Force $tarball -ErrorAction SilentlyContinue
    }
}
