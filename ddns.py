
"""updating IP v4 and v6 of dns entry when they have changed"""

import os
import sys
import requests
from cloudflare import Cloudflare, CloudflareError


ZONE_ID = os.environ.get("CLOUDFLARE_ZONE_ID")
DNS_RECORD_ID_IPV4 =os.environ.get("CLOUDFLARE_DNS_RECORD_ID_IPV4")
DNS_RECORD_ID_IPV6 = os.environ.get("CLOUDFLARE_DNS_RECORD_ID_IPV6")
REQUEST_TIMEOUT_DURATION_S = 20


client = Cloudflare(
    api_email=os.environ.get("CLOUDFLARE_EMAIL"),
    api_key=os.environ.get("CLOUDFLARE_API_KEY"),
    api_token=os.environ.get("CLOUDFLARE_API_TOKEN"),
)


try:
    old_ipv4 = client.dns.records.get(dns_record_id=DNS_RECORD_ID_IPV4, zone_id=ZONE_ID)
    old_ipv6 = client.dns.records.get(dns_record_id=DNS_RECORD_ID_IPV6, zone_id=ZONE_ID)

    print(old_ipv4.content)
    print(old_ipv6.content)

    new_ipv4_response = requests.get('https://api.ipify.org', timeout=REQUEST_TIMEOUT_DURATION_S)
    new_ipv6_response = requests.get('https://api64.ipify.org', timeout=REQUEST_TIMEOUT_DURATION_S)

    new_ipv4 = new_ipv4_response.text
    new_ipv6 = new_ipv6_response.text

    if old_ipv4 != new_ipv4:
        print(f"setting new IP v4: {old_ipv4} --> {new_ipv4}")
        client.dns.records.edit(
            dns_record_id=DNS_RECORD_ID_IPV4,
            zone_id=ZONE_ID,
            content=new_ipv4,
            name=old_ipv4.name,
            type=old_ipv4.type)
    else:
        print("IP v4 not changed")

    if old_ipv6 != new_ipv6:
        print(f"setting new IP v6: {old_ipv6} --> {new_ipv6}")
        client.dns.records.edit(
            dns_record_id=DNS_RECORD_ID_IPV6,
            zone_id=ZONE_ID,
            content=new_ipv6,
            name=old_ipv6.name,
            type=old_ipv6.type)
    else:
        print("IP v6 not changed")
except CloudflareError as e:
    sys.stderr.write('api error\n')
    sys.exit(e)
else:
    sys.exit(0)
