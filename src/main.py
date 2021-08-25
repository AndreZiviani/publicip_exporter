#!/usr/bin/env python3
import datetime
import os
from prometheus_client import make_wsgi_app, Info
from flask import Flask
from waitress import serve
import dns.resolver
from ipwhois import IPWhois

app = Flask("PublicIP-Exporter")  # Create flask app

# Create Metrics
ipv4 = Info('public_ip_v4', 'Public IPv4')
ipv6 = Info('public_ip_v6', 'Public IPv6')


def log(msg):
    current_dt = datetime.datetime.now()
    print(current_dt.strftime("%d/%m/%Y %H:%M:%S - ") + msg)


def get_asn(ip):
    o = IPWhois(ip)

    return o.ipasn.lookup()


def get_ip():
    my_ipv4 = {}
    my_ipv6 = {}

    opendns_v4 = dns.resolver.resolve('resolver1.opendns.com.', 'A')
    opendns_v6 = dns.resolver.resolve('resolver1.opendns.com.', 'AAAA')

    resolver = dns.resolver.Resolver()

    try:
        resolver.nameservers = [opendns_v4[0].to_text()]
        address = resolver.resolve('myip.opendns.com', 'A')[0].to_text()
        my_ipv4 = get_asn(address)
        my_ipv4["address"] = address
    except dns.exception.Timeout:
        log("ERROR: Timeout querying the IPv4 DNS server")
        my_ipv4["address"] = "<Timeout>"

    try:
        resolver.nameservers = [opendns_v6[0].to_text()]
        address = resolver.resolve('myip.opendns.com', 'AAAA')[0].to_text()
        my_ipv6 = get_asn(address)
        my_ipv6["address"] = address
    except (dns.exception.Timeout, dns.resolver.NoNameservers):
        log("ERROR: Timeout querying the IPv6 DNS server")
        my_ipv6["address"] = "<Timeout>"

    return my_ipv4, my_ipv6


@app.route("/metrics")
def updateResults():
    my_ipv4, my_ipv6 = get_ip()
    ipv4.info(my_ipv4)
    ipv6.info(my_ipv6)
    current_dt = datetime.datetime.now()
    print(
        current_dt.strftime("%d/%m/%Y %H:%M:%S - ") +
        f'My current ipv4 is {my_ipv4["address"]} and ipv6 is {my_ipv6["address"]}'
    )
    return make_wsgi_app()


@app.route("/")
def mainPage():
    return ("<h1>Welcome to PublicIP-Exporter.</h1>" +
            "Click <a href='/metrics'>here</a> to see metrics.")


if __name__ == '__main__':
    PORT = os.getenv('METRICS_PORT', 9798)
    print("Starting PublicIP-Exporter on http://localhost:" + str(PORT))
    serve(app, host='0.0.0.0', port=PORT)
