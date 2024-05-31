
"""updating IP of dns entry when it has changed"""

import os
import sys
import requests
from cloudflare import Cloudflare, CloudflareError


ZONE_ID = os.environ.get("CLOUDFLARE_ZONE_ID")
DNS_RECORD_ID =os.environ.get("CLOUDFLARE_DNS_RECORD_ID")
REQUEST_TIMEOUT_S = 20


client = Cloudflare(
    api_email=os.environ.get("CLOUDFLARE_EMAIL"),
    api_key=os.environ.get("CLOUDFLARE_API_KEY"),
    api_token=os.environ.get("CLOUDFLARE_API_TOKEN"),
)


try:
    # requesting old ip
    old_ip_response = client.dns.records.get(dns_record_id=DNS_RECORD_ID, zone_id=ZONE_ID)

    # requesting new ip
    if old_ip_response.type == 'A':
        new_ip_response = requests.get('https://api.ipify.org', timeout=REQUEST_TIMEOUT_S)
    elif old_ip_response.type == 'AAAA':
        new_ip_response = requests.get('https://api64.ipify.org', timeout=REQUEST_TIMEOUT_S)
    else:
        sys.stderr.write(f"IP type {old_ip_response.type} unknown\n")
        sys.exit(1)

    new_ip = new_ip_response.text

    # check if the old ip is different to the new ip and edit the dns record accordingly
    if old_ip_response.content != new_ip:
        print(f"setting new IP: {old_ip_response.content} --> {new_ip}")
        client.dns.records.edit(
            dns_record_id=DNS_RECORD_ID,
            zone_id=ZONE_ID,
            content=new_ip,
            name=old_ip_response.name,
            type=old_ip_response.type)
    else:
        print("IP not changed")

except CloudflareError as e:
    sys.stderr.write('api error\n')
    sys.exit(e)

else:
    sys.exit(0)
