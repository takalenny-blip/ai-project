param(
  [Parameter(Mandatory=$true)][string]$Url,
  [string]$Output = "$env:USERPROFILE\Dropbox\dimora\dimora-favorite-programs.json",
  [int]$Port = 9222,
  [int]$WaitSeconds = 15
)
$ErrorActionPreference = "Stop"

if($Url -match '^<.*>$'){
  throw "Url is still a placeholder. Replace <DiMORAのお気に入りURL> with the actual DiMORA favorites page URL."
}
if($Url -notmatch '^https://(www\.)?dimora\.jp/'){
  throw "Url must be a DiMORA URL beginning with https://www.dimora.jp/."
}

function Get-ChromePath {
  $candidates = @(
    "$env:ProgramFiles\Google\Chrome\Application\chrome.exe",
    "$env:ProgramFiles(x86)\Google\Chrome\Application\chrome.exe",
    "$env:LOCALAPPDATA\Google\Chrome\Application\chrome.exe",
    "$env:ProgramFiles\Microsoft\Edge\Application\msedge.exe",
    "$env:ProgramFiles(x86)\Microsoft\Edge\Application\msedge.exe"
  )
  foreach($p in $candidates){ if(Test-Path $p){ return $p } }
  throw "Chrome/Edge executable not found."
}

function Get-CdpTabs {
  try { return @(Invoke-RestMethod "http://127.0.0.1:$Port/json/list" -TimeoutSec 2) }
  catch { return @() }
}

$tabs = Get-CdpTabs
if(-not $tabs){
  $browser = Get-ChromePath
  $profile = Join-Path $env:LOCALAPPDATA "DiMORA-CDP-Profile"
  Start-Process $browser -ArgumentList "--remote-debugging-port=$Port","--user-data-dir=$profile",$Url
  Write-Host "Dedicated DiMORA browser started. Waiting for CDP..."
  for($i=0;$i -lt $WaitSeconds;$i++){
    Start-Sleep -Seconds 1
    $tabs = Get-CdpTabs
    if($tabs.Count -gt 0){ break }
  }
  if($tabs.Count -eq 0){ throw "CDP endpoint did not become available on port $Port." }
}

$tab = $tabs | Where-Object { $_.type -eq "page" } | Select-Object -First 1
if(-not $tab){ throw "No debuggable page found on port $Port." }

Add-Type -AssemblyName System.Net.WebSockets
$ws=[System.Net.WebSockets.ClientWebSocket]::new()
$ws.ConnectAsync([Uri]$tab.webSocketDebuggerUrl,[Threading.CancellationToken]::None).GetAwaiter().GetResult()
$script:Id=0

function Invoke-Cdp([string]$method,[hashtable]$params=@{}){
  $script:Id++
  $msg=@{id=$script:Id;method=$method;params=$params}|ConvertTo-Json -Compress
  $bytes=[Text.Encoding]::UTF8.GetBytes($msg)
  $ws.SendAsync([ArraySegment[byte]]::new($bytes),[Net.WebSockets.WebSocketMessageType]::Text,$true,[Threading.CancellationToken]::None).GetAwaiter().GetResult()
  $buf=New-Object byte[] 1048576; $result=""
  do{
    $seg=[ArraySegment[byte]]::new($buf)
    $r=$ws.ReceiveAsync($seg,[Threading.CancellationToken]::None).GetAwaiter().GetResult()
    $result+=[Text.Encoding]::UTF8.GetString($buf,0,$r.Count)
  }while(-not $r.EndOfMessage)
  return $result|ConvertFrom-Json
}

Invoke-Cdp "Page.navigate" @{url=$Url}|Out-Null
Write-Host "Navigated dedicated browser to DiMORA URL. If login is shown, log in and rerun this command."

$deadline=(Get-Date).AddSeconds(20)
$value=$null
while((Get-Date) -lt $deadline){
  Start-Sleep -Seconds 2
  $expr='(()=>{const d=window.GL_FAVPGM_DATA;if(!d)return {found:false,reason:"GL_FAVPGM_DATA not found"};const r=Array.isArray(d.record)?d.record:(Array.isArray(d.records)?d.records:null);return {found:true,count:r?r.length:0,record:r||[]};})()'
  $res=Invoke-Cdp "Runtime.evaluate" @{expression=$expr;returnByValue=$true}
  $value=$res.result.result.value
  if($value.found -and $value.record){ break }
}

if(-not $value.found){
  Write-Host "DiMORA page is open, but GL_FAVPGM_DATA is not available yet. Complete login/page loading, then rerun."
  exit 2
}
if(-not $value.record){ throw "GL_FAVPGM_DATA found but record[] is unavailable." }

$json=$value.record|ConvertTo-Json -Depth 20
$dir=Split-Path $Output -Parent
New-Item -ItemType Directory -Force $dir|Out-Null
Set-Content -Path $Output -Value $json -Encoding UTF8
Write-Host "Captured $($value.count) DiMORA records to $Output"
