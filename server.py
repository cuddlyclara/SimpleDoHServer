#!/usr/bin/python3

"""
Name: cuddlyclara
Website: cuddlyclara.de
Source: https://github.com/cuddlyclara/SimpleDoHServer
Description: Very simple DoH server based on Python 3, which passes the client IP via ECS.
"""

import base64
import logging
import ipaddress
import http.server
import socketserver
import urllib.parse
import dns.message
import dns.edns
import dns.query

def is_valid_ipv4(ip_str):
    try:
        ipaddress.IPv4Address(ip_str)
        return True
    except ipaddress.AddressValueError:
        return False

def requestDNSAnswer(query, clientip):
    # Parse the DNS query message from wire format
    request = dns.message.from_wire(query)

    # Log DNS query details: type, domain, and client IP if available
    if len(request.question) > 0:
        question = request.question[0]
        logging.info(f'query {dns.rdatatype.to_text(question.rdtype)} {question.name.to_text()} from {clientip}')

    # Include EDNS with ECS option from client IP address if client IP address is valid
    if is_valid_ipv4(clientip):
        ecs = dns.edns.ECSOption.from_text(clientip + '/32')
        request.use_edns(edns=True, options=[ecs])
    else:
        logging.warn(f'client IP {clientip} not valid using server IP for request');

    # Send the query and return the DNS response
    response = dns.query.udp(request, dnsserver)
    return response.to_wire()

class DohHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        # Parse the dns query parameter
        query = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        dns_query = query.get('dns', [b''])[0]

        # Respond with DoH response
        self.send_response(200)
        self.send_header('Content-Type', 'application/dns-message')
        self.end_headers()
        self.wfile.write(requestDNSAnswer(base64.b64decode(dns_query), self.headers[realipheader]))

    def do_POST(self):
        # Parse input stream
        content_length = int(self.headers['Content-Length'])
        dns_query = self.rfile.read(content_length)

        # Respond with DoH response
        self.send_response(200)
        self.send_header('Content-Type', 'application/dns-message')
        self.end_headers()
        self.wfile.write(requestDNSAnswer(dns_query, self.headers[realipheader]))

# Set the LogLevel to logging.WARNING or logging.ERROR to suppress the output of DNS requests
logging.basicConfig(level=logging.INFO)

# Set the server address, port, dnsserver and the real ip header
host = '127.0.0.1'
port = 8080
dnsserver = '10.10.10.10'
realipheader = 'X-Forwarded-For'

# Create the DoH server
with socketserver.TCPServer((host, port), DohHandler) as httpd:
    try:
        print(f'Serving DoH on {host}:{port} using DNS server {dnsserver}')
        httpd.serve_forever()
    except KeyboardInterrupt:
        print('Shutting down the server...')
        httpd.shutdown()
