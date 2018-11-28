'''
Dynamic DNS for Firewall for Vultr
By MBRCTV

credit for https://github.com/andyjsmith/Vultr-Dynamic-DNS
'''
import requests
import smtplib
import json
import socket
from email.message import EmailMessage
from email.headerregistry import Address


# Import the values from the configuration file
with open("ddns_config.json") as config_file:
    config = json.load(config_file)  # Convert JSON to Python

firewallgroup = config["firewallgroup"]
api_key = config["api_key"]
user = config["user"]
server_mode = config["server_mode"]
from_email = config["from_email"]
to_email = config["to_email"]
password = config["password"]
from_name = config["from_name"]
ddns_domain = config["ddns_domain"]

# Get the public IP of the server
if server_mode == "yes":
    # your os sends out a dns query
    ip = socket.gethostbyname(ddns_domain)
else:
    ip = requests.get("https://ip.42.pl/raw").text

# Get the list of DNS records from Vultr to translate the record name to recordid
raw_rules = json.loads(requests.get("https://api.vultr.com/v1/firewall/rule_list?FIREWALLGROUPID=" +
                                    firewallgroup + "&direction=in&ip_type=v4", headers={"API-Key": api_key}).text)

# Make a new varible with the vultr ip
v_ip = ""
for rule in raw_rules:
    if raw_rules[rule]["notes"] == user:
        v_rulenumber = raw_rules[rule]["rulenumber"]
        v_notes = raw_rules[rule]["notes"]
        v_port = raw_rules[rule]["port"]
        v_protocol = raw_rules[rule]["protocol"]
        v_subnet_size = raw_rules[rule]["subnet_size"]
        v_subnet = raw_rules[rule]["subnet"]
        v_ip = v_subnet

# Cancel if no records from Vultr match the config file
if len(v_ip) == 0:
    print("Configuration error, no ip found for this user.")
    quit()

# Check if the IP address actually differs from any of the records
needsUpdated = False
if v_ip != ip:
    needsUpdated = True

# Cancel if the IP has not changed
if not needsUpdated:
    print("your ip is: " + ip +
          " \nIP address has not changed. No rules have been updated.")
    quit()

print("your IP has changed since last checking.")
print("Old IP on Vultr: " + v_ip + ", current Device IP: " + ip)

# Remove old Firewall rule
payload = {"FIREWALLGROUPID": firewallgroup, "rulenumber": v_rulenumber}
response = requests.post("https://api.vultr.com/v1/firewall/rule_delete",
                         data=payload, headers={"API-Key": api_key})
if response.status_code == 200:
    print("Current rule for " + user + " has been deleted")
else:
    print("Error deleting rule")
    quit()

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
    print("user " + user + " has been updated to " + ip)
else:
    print("Error adding rule")
    quit()

# send email report

if len(from_email) == 0:
    quit()
else:
    to_address_l = []
    
    email_text = 'user ' + user + ' has been updated to ' + ip
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
        print( "\n" .join(to_email))
    except:
        print("failed to send email")
