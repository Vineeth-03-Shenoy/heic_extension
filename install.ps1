# Registers HEIC Viewer as the handler for .heic/.heif/.hif/.avif for the
# current user (HKCU only — no admin needed). Also adds a right-click
# "Convert to JPEG" entry. Reversible with uninstall.ps1.
$ErrorActionPreference = 'Stop'

$exe = Join-Path $PSScriptRoot 'dist\HEICViewer\HEICViewer.exe'
if (-not (Test-Path $exe)) {
    Write-Error "HEICViewer.exe not found. Run .\build.ps1 first."
}

$progId = 'HEICViewer.Image'
$classes = 'HKCU:\Software\Classes'
$extensions = '.heic', '.heif', '.hif', '.avif'

function Set-Default($path, $value) {
    if (-not (Test-Path $path)) { New-Item -Path $path -Force | Out-Null }
    Set-ItemProperty -Path $path -Name '(default)' -Value $value
}

# ProgID: open verb, icon, friendly name
Set-Default "$classes\$progId" 'HEIC Image'
Set-Default "$classes\$progId\DefaultIcon" "`"$exe`",0"
Set-Default "$classes\$progId\shell" 'open'
Set-Default "$classes\$progId\shell\open" 'Open with HEIC Viewer'
Set-Default "$classes\$progId\shell\open\command" "`"$exe`" `"%1`""
Set-Default "$classes\$progId\shell\tojpeg" 'Convert to JPEG'
Set-Default "$classes\$progId\shell\tojpeg\command" "`"$exe`" --convert `"%1`""

foreach ($ext in $extensions) {
    Set-Default "$classes\$ext" $progId
    if (-not (Test-Path "$classes\$ext\OpenWithProgids")) {
        New-Item -Path "$classes\$ext\OpenWithProgids" -Force | Out-Null
    }
    Set-ItemProperty -Path "$classes\$ext\OpenWithProgids" -Name $progId -Value ''
    # "Convert to JPEG" in the right-click menu regardless of default app
    Set-Default "$classes\SystemFileAssociations\$ext\shell\tojpeg" 'Convert to JPEG'
    Set-Default "$classes\SystemFileAssociations\$ext\shell\tojpeg\command" "`"$exe`" --convert `"%1`""
}

# Register under App Paths so "Open with" can find it by name
Set-Default "HKCU:\Software\Microsoft\Windows\CurrentVersion\App Paths\HEICViewer.exe" $exe

# Tell Explorer that file associations changed
Add-Type -Namespace Win32 -Name Shell -MemberDefinition @'
[System.Runtime.InteropServices.DllImport("shell32.dll")]
public static extern void SHChangeNotify(int wEventId, int uFlags, System.IntPtr dwItem1, System.IntPtr dwItem2);
'@
[Win32.Shell]::SHChangeNotify(0x08000000, 0x0000, [System.IntPtr]::Zero, [System.IntPtr]::Zero)

Write-Host "Registered HEIC Viewer for: $($extensions -join ', ')"
Write-Host ""
Write-Host "If Windows still opens another app by default:"
Write-Host "  right-click a .heic file -> Open with -> Choose another app ->"
Write-Host "  HEIC Image / HEIC Viewer -> tick 'Always'."
