param(
  [Parameter(Mandatory=$true)][string]$Url,
  [string]$Output = "$env:USERPROFILE\Dropbox\dimora\dimora-favorite-programs.json",
  [int]$Port = 9222
)
$ErrorActionPreference = "Stop"
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
$tabs=$null
try { $tabs=Invoke-RestMethod "http://127.0.0.1:$Port/json/list" -TimeoutSec 2 } catch {}
if(-not $tabs){
  $browser=Get-ChromePath
  $profile=Join-Path $env:LOCALAPPDATA "DiMORA-CDP-Profile"
  Start-Process $browser -ArgumentList "--remote-debugging-port=$Port","--user-data-dir=$profile",$Url
  Write-Host "Dedicated browser profile opened. If DiMORA asks for login, log in there, then rerun."
  exit 2
}
$tab=$tabs | Where-Object {$_.type -eq "page"} | Select-Object -First 1
if(-not $tab){throw "No debuggable page found on port $Port."}
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
  do{$seg=[ArraySegment[byte]]::new($buf);$r=$ws.ReceiveAsync($seg,[Threading.CancellationToken]::None).GetAwaiter().GetResult();$result+=[Text.Encoding]::UTF8.GetString($buf,0,$r.Count)}while(-not $r.EndOfMessage)
  return $result|ConvertFrom-Json
}
Invoke-Cdp "Page.navigate" @{url=$Url}|Out-Null
Start-Sleep -Seconds 3
$expr='(()=>{const d=window.GL_FAVPGM_DATA;if(!d)return {found:false,reason:"GL_FAVPGM_DATA not found"};const r=Array.isArray(d.record)?d.record:(Array.isArray(d.records)?d.records:null);return {found:true,count:r?r.length:0,record:r||[]};})()'
$res=Invoke-Cdp "Runtime.evaluate" @{expression=$expr;returnByValue=$true}
$value=$res.result.result.value
if(-not $value.found){throw $value.reason}
if(-not $value.record){throw "GL_FAVPGM_DATA found but record[] is unavailable."}
$json=$value.record|ConvertTo-Json -Depth 20
$dir=Split-Path $Output -Parent
New-Item -ItemType Directory -Force $dir|Out-Null
Set-Content -Path $Output -Value $json -Encoding UTF8
Write-Host "Captured $($value.count) DiMORA records to $Output"
