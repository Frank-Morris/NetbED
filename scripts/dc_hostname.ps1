Write-Host Current host name is set to $env:COMPUTERNAME

$hostname = "Client"

if ($env:COMPUTERNAME -ne $hostname) {
    Write-Host "Current name: $env:COMPUTERNAME"
    Write-Host "Renaming computer name to '$hostname'..."
    Rename-Computer -NewName $hostname -Force
    Write-Warning "Hostname has been succesffully changed, a reboot is required for this to take affect..."
}else{
    Write-Host "Hostname is already correctly set to '$hostname'."
}