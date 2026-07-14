# Removes everything install.ps1 added (HKCU only).
$ErrorActionPreference = 'SilentlyContinue'

$classes = 'HKCU:\Software\Classes'
$progId = 'HEICViewer.Image'
$extensions = '.heic', '.heif', '.hif', '.avif'

Remove-Item -Path "$classes\$progId" -Recurse -Force -Confirm:$false
Remove-Item -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\App Paths\HEICViewer.exe" -Recurse -Force -Confirm:$false

foreach ($ext in $extensions) {
    $key = "$classes\$ext"
    if (Test-Path $key) {
        $default = (Get-ItemProperty -Path $key).'(default)'
        if ($default -eq $progId) { Set-ItemProperty -Path $key -Name '(default)' -Value '' }
        Remove-ItemProperty -Path "$key\OpenWithProgids" -Name $progId -Force -Confirm:$false
    }
    Remove-Item -Path "$classes\SystemFileAssociations\$ext\shell\tojpeg" -Recurse -Force -Confirm:$false
}

Add-Type -Namespace Win32 -Name Shell -MemberDefinition @'
[System.Runtime.InteropServices.DllImport("shell32.dll")]
public static extern void SHChangeNotify(int wEventId, int uFlags, System.IntPtr dwItem1, System.IntPtr dwItem2);
'@
[Win32.Shell]::SHChangeNotify(0x08000000, 0x0000, [System.IntPtr]::Zero, [System.IntPtr]::Zero)

Write-Host "HEIC Viewer file associations removed."
