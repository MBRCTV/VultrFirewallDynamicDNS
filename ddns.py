"""
Dynamic DNS for Firewall for Vultr
By MBRCTV

credit for https://github.com/andyjsmith/Vultr-Dynamic-DNS
"""
import sys

import requests
import smtplib
import json
import socket
from email.message import EmailMessage
from email.headerregistry import Address
import logging
import yaml
from logging.config import dictConfig

with open('logging.yaml', 'r') as f:
    log_cfg = yaml.safe_load(f.read())

dictConfig(log_cfg)
logger = logging.getLogger(__name__)
# Import the values from the configuration file
with open("ddns_config.json") as config_file:
    config = json.load(config_file)  # Convert JSON to Python

firewalls = config.get("firewalls")
global_api_key = config.get("api_key")
global_email = config.get("email")

if __name__ == '__main__':

    for fw in firewalls:
        firewallgroup = fw.get("firewallgroup")
        notes = fw.get("notes")
        ddns_domain = fw.get("ddns_domain")
        api_key = fw.get("api_key")
        email = fw.get("email")

        logger.debug("checking for firewall group %s for notes %s ", firewallgroup, notes)

        if not api_key:
            api_key = global_api_key

        # Get the public IP of the server
        if ddns_domain:
            # your os sends out a dns query
            ip = socket.gethostbyname(ddns_domain)
        else:
            ip = requests.get("https://api.ipify.org/").text

        # Get the list of DNS records from Vultr to translate the record name to recordid
        raw_rules = json.loads(requests.get("https://api.vultr.com/v1/firewall/rule_list?FIREWALLGROUPID=" +
                                            firewallgroup + "&direction=in&ip_type=v4", headers={"API-Key": api_key}).text)

        # Make a new varible with the vultr ip
        v_ip = None
        for rule in raw_rules:
            if raw_rules[rule]["notes"] == notes:
                v_rulenumber = raw_rules[rule]["rulenumber"]
                v_notes = raw_rules[rule]["notes"]
                v_port = raw_rules[rule]["port"]
                v_protocol = raw_rules[rule]["protocol"]
                v_subnet_size = raw_rules[rule]["subnet_size"]
                v_subnet = raw_rules[rule]["subnet"]
                v_ip = v_subnet

                # Cancel if no records from Vultr match the config file
                if not v_ip:
                    logger.warning("Configuration error, no ip found for note %s.", notes)
                    continue

                # Check if the IP address actually differs from any of the records
                needsUpdated = False
                if v_ip != ip:
                    needsUpdated = True

                # Cancel if the IP has not changed
                if not needsUpdated:
                    logger.info("your ip is: %s", ip)
                    logger.info("IP address has not changed. No rules has been updated.")
                    continue

                logger.info("your IP has changed since last checking.")
                logger.info("Old IP on Vultr: %s, current Device IP: %s", v_ip, ip )

                # Remove old Firewall rule
                payload = {"FIREWALLGROUPID": firewallgroup, "rulenumber": v_rulenumber}
                response = requests.post("https://api.vultr.com/v1/firewall/rule_delete",
                                         data=payload, headers={"API-Key": api_key})
                if response.status_code == 200:
                    logger.info("Current rule for %s for port %s has been deleted ", notes, v_port)
                else:
                    logger.warning("Error deleting rule for %s", firewallgroup)
                    continue

                # Update the rule in Vultr with the new IP address
                payload = {"FIREWALLGROUPID": firewallgroup,
                           "direction": "in",
                                        "ip_type": "v4",
                                        "protocol": v_protocol,
                                        "subnet": ip,
                                        "subnet_size": v_subnet_size,
                                        "port": v_port,
                                        "notes": v_notes}
                response = requests.post("https://api.vultr.com/v1/firewall/rule_create",
                                         data=payload, headers={"API-Key": api_key})
                if response.status_code == 200:
                    logger.info("user %s has been updated to %s", notes, ip)
                else:
                    logger.warning("Error adding rule for %s", firewallgroup)
                    continue

        if email:
            from_email = email.get("email")
            to_email = email.get("to_email")
            password = email.get("password")
            from_name = email.get("from_name")
        else:
            from_email = global_email.get("email")
            to_email = global_email.get("to_email")
            password = global_email.get("password")
            from_name = global_email.get("from_name")

        # send email report
        if not from_email:
            logger.info("No emails for this firewall.. skipping..")
            continue
        else:
            to_address_l = []

        email_text = f'user {notes} has been updated to {ip}'
        msg = EmailMessage()
        msg.set_content(email_text)
        msg['Subject'] = '[VultrIP] IP UPDATE'
        msg['From'] = 'SCRIPT NOTIFICATION'
        msg['To'] = ', '.join(to_email)

        try:
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.ehlo()
            server.starttls()
            server.login(from_email, password)
            server.send_message(msg)
            server.close()
            print('successfully sent the email to: ')
            print("\n" .join(to_email))
        except:
            print("failed to send email")
