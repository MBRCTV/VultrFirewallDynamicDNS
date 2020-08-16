# Dynamic IP update for vultr Firewall


This script was intended to be able to use vultr firewall and block all IPs and only whitelist your own IP. \
because vultr don't accept a dynamic DDNS domain (like [no-ip](https://www.noip.com/))

This script will update vultr with your new ip every time it changes

for example i have a freepbx server running in vultr so i set a firewall to only allow my location to access the server

### Setup

Assuming you have a vultr account (if you dont have one you can use [my affiliate link](https://www.vultr.com/?ref=8519411-6G) and Get $100 for the first 30 days)

* go to the firewall tab, and click 'Add Firewall Group'
* select the protocol you would like to open for yourself like TCP 
* enter the port or range for example `1 - 65535`	
* select one source the ip (not important as the script will update it 
* IMPORTANT, add a any word as a note to your rule, so the api can find it, for example i use my username `mbrctv`


### Config

`api_key` vultr api key \
`firewallgroup` the firewall ID \
`notes` the note you added for reference \
`ddns_domain` (Optional) the ddns domain if you have \
`from_email` (Optional) if you want email notification each time the IP changed \
`password` (Optional) emails password \
`to_email` (Optional) array of emails (can be array with only 1 email) \
`from_name` (Optional) sender name

you can set `api_key` as global, or set it for each firewall rule
you can set `email or in global or for each firewall`


### Windows Task
Create a task in Task Scheduler to run every 30 minutes. Follow the Microsoft guide for basic task creation.

Open Task Scheduler and click "Create Task...".
Give it a name and create a new trigger.
Click "Daily". Under "Advanced Settings" click to repeat the task every 30 minutes and change "for a duration of" to "Indefinitely".
Add a new action to start a program and browse to your Python executable. Add the ddns.py script as an argument.

### Linux Cronjob

comming soon


credit for https://github.com/andyjsmith/Vultr-Dynamic-DNS
