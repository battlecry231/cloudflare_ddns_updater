
"""updating IP of dns entry when it has changed"""

import logging
import os
import sys
from cloudflare import Cloudflare, APIError
from systemd.journal import JournalHandler
from fritzconnection.lib.fritzstatus import FritzStatus
import netifaces


ZONE_ID = os.environ.get('CLOUDFLARE_ZONE_ID')
DNS_RECORD_ID =os.environ.get('CLOUDFLARE_DNS_RECORD_ID')


client = Cloudflare(
    api_email=os.environ.get('CLOUDFLARE_EMAIL'),
    api_key=os.environ.get('CLOUDFLARE_API_KEY'),
    api_token=os.environ.get('CLOUDFLARE_API_TOKEN'),
)

log = logging.getLogger('cloudflare_ddns_updater')
log.addHandler(JournalHandler())
log.setLevel(logging.INFO)

try:
    # requesting old ip
    old_ip_response = client.dns.records.get(dns_record_id=DNS_RECORD_ID, zone_id=ZONE_ID)

    # requesting new ip
    if old_ip_response.type == 'A':
        fritz_status = FritzStatus(
            address=os.getenv('FRITZBOX_ADDRESS')
        )
        new_ip = fritz_status.external_ip
    elif old_ip_response.type == 'AAAA':
        new_ip = ''
        addresses = netifaces.ifaddresses(os.getenv('NETWORK_INTERFACE_NAME'))
        if netifaces.AF_INET6 in addresses:
            ipv6_addresses = addresses[netifaces.AF_INET6]
            # Filter out link-local addresses (starts with 'fe80')
            for ipv6_info in ipv6_addresses:
                if 'addr' in ipv6_info and not ipv6_info['addr'].startswith('fe80'):
                    new_ip = ipv6_info['addr']
        if new_ip == '':
            sys.exit(2)
    else:
        log.error('IP type %s unknown', old_ip_response.type)
        sys.exit(1)

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
