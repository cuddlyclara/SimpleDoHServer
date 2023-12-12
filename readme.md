# Introduction

This Python3 script serves as a very simple DNS over HTTPS (DoH) server. It should be used behind a reverse proxy, which takes care of the HTTPS configuration.

The goal of this script is to pass the client IP of the requesting client to the DNS server. For this to work, the reverse proxy must pass this information to the script via an HTTP header. Subsequently, this information will be added to the DNS query using the EDNS Client Subnet (ECS). DNS servers such as Pi-hole can be [configured in this way](https://docs.pi-hole.net/ftldns/configfile/#block_edns0_ecs) to process these details in logs or display them in the web interface.

# Why?

The use of Encrypted Client Hello (ECH) often requires the activation of DoH. If a network-wide technology for encrypting all DNS queries is already in use (e.g., [dnscrypt-proxy](https://github.com/DNSCrypt/dnscrypt-proxy)) in conjunction with a DNS-based ad blocker like [Pi-hole](https://pi-hole.net/), it is necessary to set up a local DoH server to avoid the need to bypass any local systems.

# Dependencies

To parse DNS messages, the Python library "dnspython" is used, which can be installed if necessary with the following command:

```bash
pip3 install dnspython
```

# Configuration

Settings are defined using variables within the script. By default, the server uses port 8080 on localhost. The DNS server used here is set as an example to the IP address 10.10.10.10 and need to be replaced with the IP address of your local DNS server. Additionally, the dns request timeout and the header containing the real client IP can be modified as needed.

```python
# Set the server address, port, dns server, dns request timeout (in seconds) and the real ip header
host = '127.0.0.1'
port = 8080
dnsserver = '10.10.10.10'
timeout = 10
realipheader = 'X-Forwarded-For'
```

For reduced logging, it's advisable to set the LogLevel to something like `logging.WARNING`, for instance.

```bash
# Set the LogLevel to logging.WARNING or logging.ERROR to suppress the output of DNS requests
logging.basicConfig(level=logging.WARNING)
```

# Execution

Since all options are already set within the script, you can easily start the script from the command line:

```bash
./server.py
```

Before running the script, it may be necessary to make the script executable:

```bash
chmod +x server.py
```

A recommended approach is to run this as a service using Systemd.

# Troubleshooting

By default, Pi-hole uses the web server Lighttpd. Up to and including version 1.4.59, the web server responded to empty HTTP headers with a response code of 400. This prevented Firefox from sending requests to the DoH server behind the Lighttpd server due to its default empty "Accept-Encoding" header in DoH requests. This issue was fixed in [this commit](https://github.com/lighttpd/lighttpd1.4/commit/262561f). Unfortunately, older Debian servers cannot update to a Lighttpd version >= 1.4.60. One possible workaround is to set the switch `network.trr.send_empty_accept-encoding_headers` to `false` under `about:config`.

# Security

Since this is just a simple implementation of a DoH server with minimal input validation, it's best to use this server only in its intended environment, such as within a local network.
