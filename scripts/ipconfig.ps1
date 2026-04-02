 Write-Host "Vagrant is running shell scrip to configure the static ip address."
 $staticIp = "10.0.1.3"
      $subnet = 24
      $gateway = "10.0.1.1"
      $dns = "10.0.1.2"
      $metric = 10

    
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
                       
         Set-DnsClientServerAddress -InterfaceIndex $adapter.InterfaceIndex -ServerAddresses $dns
                      
         Write-Host "Forcing Windows to stop auto-calculating the metric..."
         # 1. Turn off Automatic Metric using "Disabled" instead of $false
         Set-NetIPInterface -InterfaceIndex $adapter.InterfaceIndex -AutomaticMetric Disabled -InterfaceMetric 10

         # 2. Force the Default Gateway Route to 1 ( set preference route )
         Set-NetRoute -DestinationPrefix "0.0.0.0/0" -InterfaceIndex $adapter.InterfaceIndex -RouteMetric 1 -ErrorAction SilentlyContinue

         # 3. Hard Isolation: Delete the Vagrant NAT 'Backdoor' Gateway route
         Write-Host "Disabling default vagrant NAT route"
         Remove-NetRoute -DestinationPrefix "0.0.0.0/0" -NextHop "10.0.2.2" -Confirm:$false -ErrorAction SilentlyContinue

     } else {
        Write-Error "No valid adapter has been located" 
     }
   