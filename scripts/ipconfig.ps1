 Write-Host "Vagrant is running shell scrip to configure the static ip address."
 $staticIp = "10.0.1.3"
      $subnet = 24
      $gateway = "10.0.1.1"

    
      #Look for interface not named "Ethernet", and make sure the interface is up, place the object into $adapter container
      $adapter = Get-NetAdapter | Where-Object { $_.InterfaceAlias -ne "Ethernet" -and $_.Status -eq "Up" }

      if ($adapter) {
         Write-Host "Getting Adapter: $($adapter.InterfaceAlias)"
         #Look inside the $adapter container inside the object, find the interface ID inside the object and use that for removing the IP config, confirm automatically and if the IP address was already empty, ignore the error and continue.
         Remove-NetIPAddress -InterfaceIndex $adapter.InterfaceIndex -Confirm:$false -ErrorAction SilentlyContinue

         #Look inside the $adapter container, inside the object, find the associated interface ID and assign the new IP configuration for that interface
         New-NetIPAddress -InterfaceIndex $adapter.InterfaceIndex `
                       -IPAddress $staticIp `
                       -PrefixLength $subnet `
                       -DefaultGateway $gateway
     } else {
        Write-Error "You have fecked up" 
     }
   