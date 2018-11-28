# vultrFirewallDynamicDNS

Create a task in Task Scheduler to run every 30 minutes. Follow the Microsoft guide for basic task creation.

Open Task Scheduler and click "Create Task...".
Give it a name and create a new trigger.
Click "Daily". Under "Advanced Settings" click to repeat the task every 30 minutes and change "for a duration of" to "Indefinitely".
Add a new action to start a program and browse to your Python executable. Add the ddns.py script as an argument.

credit for https://github.com/andyjsmith/Vultr-Dynamic-DNS

