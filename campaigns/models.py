from django.db import models

class Subscriber(models.Model):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30, blank=True)
    is_active = models.BooleanField(default=True) # true when subscribed
    subscribed_at = models.DateTimeField(auto_now_add=True) # the first time subscription
    unsubscribed_at = models.DateTimeField(null=True, blank=True)
    resubscribed_at = models.DateTimeField(null=True, blank=True) # when user unsubscribes and later re-subscribes again

    def __str__(self):
        return self.email

class Campaign(models.Model):
    subject = models.CharField(max_length=200)
    preview_text = models.CharField(max_length=250, blank=True)
    article_url = models.URLField(blank=True)
    html_content = models.TextField()
    plain_text_content = models.TextField()
    published_date = models.DateField()

    def __str__(self):
        return f"{self.subject} ({self.published_date})"
    
class SentEmail(models.Model):
    STATUS_CHOICES = [
        ('sent', 'Sent'),
        ('failed', 'Failed'),
    ]
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE)
    subscriber = models.ForeignKey(Subscriber, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    response = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.campaign.subject} mail to {self.subscriber.email} ({self.status})"