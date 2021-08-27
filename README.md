# PublicIP Exporter

A simple Prometheus exporter that tracks your public ipv4 and ipv6 address and you ISP information (from `whois`), usefull to track failover events on systems that don't expose metrics (Ubiquity....).

## Metrics Sample

Metrics are exposed as Gauge type with the value being the ASN of your ISP.

```
public_ip_v4{address="x.x.x.x",asn="1234",asn_cidr="x.x.x.x/yy",asn_country_code="??",asn_date="YYYY-MM-DD",asn_description="ASN Description",asn_registry="nic"} 1234.0
public_ip_v6{address="x:x:x:x:x:x:x:x",asn="1234",asn_cidr="x:x:x:x:x:x:x:x/yy",asn_country_code="??",asn_date="YYYY-MM-DD",asn_description="ASN Description",asn_registry="nic"} 1234.0
```

## Grafana Annotations

If you would like to add an annotation event to Grafana Dashboards when a failover occurs (or when your ip changes) the following query/search expression can be usefull, 
it will create a single line instead of an annotation range.

```
public_ip_v4 unless (public_ip_v4 offset 1m)
```
