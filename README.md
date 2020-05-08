# Dynamic IP update for vultr Firewall


This script was intended to be able to use vultr firewall and block all IPs and only whitelist your own IP.
becouse vultr don't accept a dynamic DDNS domain (like [no-ip](https://www.noip.com/))

This script will update vultr with your new ip everytime it changes


## Setup

Assuming you have a vultr account (if you dont have one you can use [my affiliate link](https://www.vultr.com/?ref=8519411-6G) and Get $100 for the first 30 days)

* go to the firewall tab, and click 'Add Firewall Group'
* select the protocol you would like to open for yourself like TCP 
* enter the port or range for example `1 - 65535`	
* select on source the ip (not important as the script will update it 
* IMPORTANT, add a any word as a note to your rule, so the api can find it


#### Windows Task
Create a task in Task Scheduler to run every 30 minutes. Follow the Microsoft guide for basic task creation.

Open Task Scheduler and click "Create Task...".
Give it a name and create a new trigger.
Click "Daily". Under "Advanced Settings" click to repeat the task every 30 minutes and change "for a duration of" to "Indefinitely".
Add a new action to start a program and browse to your Python executable. Add the ddns.py script as an argument.

### Linux Cronjob

comming soon


credit for https://github.com/andyjsmith/Vultr-Dynamic-DNS

