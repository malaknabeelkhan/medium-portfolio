
documents = [
    {
        "id": "D1",
        "title": "Wi-Fi Connectivity Troubleshooting",
        "content": """
        Wi-Fi connectivity problems can occur because of incorrect network
        settings, weak wireless signals, router problems, or outdated network
        drivers.

        First, verify that Wi-Fi is enabled on the computer and airplane
        mode is disabled. Check whether other devices can connect to the
        same wireless network. If other devices also fail, the problem may
        be related to the router or internet connection.

        If only one computer is affected, disconnect from the wireless
        network and reconnect by entering the correct password. Restart
        the computer and router if the connection still fails.

        Open Command Prompt and run ipconfig. Check whether the wireless
        adapter has a valid IPv4 address and default gateway. An address
        beginning with 169.254 usually indicates that the computer did
        not receive an IP address from DHCP.

        If necessary, update or reinstall the wireless network adapter
        driver through Device Manager. Contact the network administrator
        if the problem persists.
        """
    },
    {
        "id": "D2",
        "title": "Printer Troubleshooting",
        "content": """
        A printer may stop printing because of power issues, disconnected
        cables, incorrect printer selection, driver problems, or a stuck
        print queue.

        First, verify that the printer is powered on and has no visible
        error indicators. Check the USB or network cable connection.
        For network printers, confirm that the printer and computer are
        connected to the appropriate network.

        Open Windows Settings and navigate to Bluetooth and devices,
        then Printers and scanners. Verify that the correct printer is
        selected and that it is not offline or paused.

        Open the print queue and cancel any stuck jobs. The Windows
        Print Spooler service manages print jobs. If printing remains
        unsuccessful, restart the Print Spooler service through the
        Services management console.

        If the printer is still unavailable, check its driver in
        Device Manager or reinstall the correct manufacturer driver.
        Print a test page to verify whether the issue is resolved.
        """
    },
    {
        "id": "D3",
        "title": "Windows Password Reset",
        "content": """
        Users may be unable to sign in to Windows because of an incorrect
        password, an expired password, a locked account, or network
        connectivity problems affecting domain authentication.

        First, verify that the correct username and password are being
        entered. Check the keyboard layout and Caps Lock status. For
        domain accounts, ensure the computer has network connectivity
        to the organization's authentication services.

        If the password has expired, follow the organization's approved
        password-change procedure. Users should use the official
        self-service password reset portal if one is available.

        If an account is locked, an authorized IT administrator can
        inspect the account status in Active Directory Users and
        Computers and unlock it according to company policy.

        If the user still cannot sign in, check whether other users
        can access the same computer and whether the issue affects
        one account or multiple accounts. Escalate persistent
        authentication failures to the system administrator.
        """
    },
    {
        "id": "D4",
        "title": "DNS Resolution Troubleshooting",
        "content": """
        DNS translates domain names into IP addresses. If DNS resolution
        fails, users may be unable to access websites or internal
        services by their hostnames even when network connectivity exists.

        First, verify that the computer has a valid IP address, subnet
        mask, default gateway, and DNS server. Run ipconfig /all in
        Command Prompt to inspect the network configuration.

        Test basic connectivity by pinging the default gateway.
        Then run nslookup followed by a domain name to check whether
        the configured DNS server can resolve it.

        If name resolution fails, inspect the configured DNS server.
        An incorrect or unreachable DNS server can prevent hostname
        resolution. Use the organization's approved DNS settings.

        You can clear the local DNS resolver cache by running
        ipconfig /flushdns. If the issue continues, investigate DNS
        server availability and escalate persistent failures to the
        network administrator.
        """
    }
]
