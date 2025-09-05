# Email Campaign Manager  

### My Approach  

- started with django proj + campaigns app  
- made models (Subscriber, Campaign, SentEmail)  
- setup admin to add records easily  
- then implemented APIs → subscribe + unsubscribe  
- added dryrun email fn (for testing purpose)  
- brought in smtp creds (mailgun test works)  
- then implemented the pub-sub model → queue + worker threads  
- workers retry if mail fails, log result in db  
- final step = mgmt command `send_daily_campaigns` which sends to all active subs for today’s/specified date's campaigns  

### Workflow 

1. add campaign in admin
2. users subscribe/unsubcribe
3. run `python manage.py send_daily_campaigns`  
4. queue fills with jobs → worker threads consume → mails sent/logged  