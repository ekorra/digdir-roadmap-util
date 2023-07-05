# digdir-roadmap-util
util for getting info from digdirs roadmap on Github, and display it as csv or json 


### Token and scopes 
Scopes: read:project
Environment property: DIGIDIR_ROADMAP_TOKEN

# Rlease  
Scopes: Contents - Read and Write, Metadata - Read
Environment property: RELEASE_TOKEN

### Scheduling

#### Github action
File: action.yml
Format: {minute}{hour}{day}{month}{day}
Sample: '0 12 * * 1' - At 12:00 on Monday

#### Azure funcion Timer trigger
File: function.json
Format: {second}{minute}{hour}{day}{month}{day}
Sample: '0 0 12 * * 1' - At 12:00 on Monday

Form help use [crontab guru] (https://crontab.guru/)

### Mail
Its possible to send notification mail to defined receipients.
The Azuere function will send mail containing the roadmap report as a CSV
The Github action will send mail with link to the github release containing the CSV report as an asset

Receipients for both jobs are defined in the mailreceipients.txt file. One line per email adress

Mails are sendt with gmail smtp account username and password for the account must be set in the environment settings properties 

SMTP_ACCOUNT
SMTP_PASSWORD
