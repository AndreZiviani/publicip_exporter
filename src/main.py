#!/usr/bin/env python3
import datetime
import os
from prometheus_client import make_wsgi_app, Gauge
from flask import Flask
from waitress import serve
import dns.resolver
from ipwhois import IPWhois

app = Flask("PublicIP-Exporter")  # Create flask app

labels = {
    'address': '0.0.0.0',
    'asn_registry': 'nic',
    'asn': '000000',
    'asn_cidr': '0.0.0.0/0',
    'asn_country_code': '??',
    'asn_date': 'YYYY-MM-DD',
    'asn_description': 'ASN Description'
}

# Create Metrics
ipv4 = Gauge('public_ip_v4', 'Public IPv4', labels.keys())
ipv6 = Gauge('public_ip_v6', 'Public IPv6', labels.keys())


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
        my_ipv4 = labels
        my_ipv4["address"] = "<Timeout>"

    try:
        resolver.nameservers = [opendns_v6[0].to_text()]
        address = resolver.resolve('myip.opendns.com', 'AAAA')[0].to_text()
        my_ipv6 = get_asn(address)
        my_ipv6["address"] = address
    except (dns.exception.Timeout, dns.resolver.NoNameservers):
        log("ERROR: Timeout querying the IPv6 DNS server")
        my_ipv6 = labels
        my_ipv6["address"] = "<Timeout>"

    return my_ipv4, my_ipv6


@app.route("/metrics")
def updateResults():
    my_ipv4, my_ipv6 = get_ip()
    ipv4.labels(**my_ipv4).set(my_ipv4['asn'])
    ipv6.labels(**my_ipv6).set(my_ipv6['asn'])
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
