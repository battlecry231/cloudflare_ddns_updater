
"""updating IP of dns entry when it has changed"""

import logging
import os
import sys
import requests
from cloudflare import Cloudflare, APIError
from systemd.journal import JournalHandler


ZONE_ID = os.environ.get("CLOUDFLARE_ZONE_ID")
DNS_RECORD_ID =os.environ.get("CLOUDFLARE_DNS_RECORD_ID")
REQUEST_TIMEOUT_S = 20


client = Cloudflare(
    api_email=os.environ.get("CLOUDFLARE_EMAIL"),
    api_key=os.environ.get("CLOUDFLARE_API_KEY"),
    api_token=os.environ.get("CLOUDFLARE_API_TOKEN"),
)

log = logging.getLogger('cloudflare_ddns_updater')
log.addHandler(JournalHandler())
log.setLevel(logging.INFO)

try:
    # requesting old ip
    old_ip_response = client.dns.records.get(dns_record_id=DNS_RECORD_ID, zone_id=ZONE_ID)

    # requesting new ip
    if old_ip_response.type == 'A':
        new_ip_response = requests.get('https://api.ipify.org', timeout=REQUEST_TIMEOUT_S)
    elif old_ip_response.type == 'AAAA':
        new_ip_response = requests.get('https://api64.ipify.org', timeout=REQUEST_TIMEOUT_S)
    else:
        log.error("IP type %s unknown", old_ip_response.type)
        sys.exit(1)

    new_ip = new_ip_response.text

    # check if the old ip is different to the new ip and edit the dns record accordingly
    if old_ip_response.content != new_ip:
        log.info('setting new IP: %s --> %s', old_ip_response.content, new_ip)
        client.dns.records.edit(
            dns_record_id=DNS_RECORD_ID,
            zone_id=ZONE_ID,
            content=new_ip,
            name=old_ip_response.name,
            type=old_ip_response.type)
    else:
        log.info('IP not changed')

except APIError as e:
    log.error('api error: %d', e.message)
    sys.exit(e)

else:
    sys.exit(0)
