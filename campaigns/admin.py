from django.contrib import admin
from .models import Subscriber, Campaign, SentEmail

@admin.register(Subscriber)
class SubscriberAdmin(admin.ModelAdmin):
    list_display = ('email', "first_name", "is_active", "subscribed_at", "resubscribed_at", "unsubscribed_at")

@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = ("subject", "published_date")

@admin.register(SentEmail)
class SentEmailAdmin(admin.ModelAdmin):
    list_display = ("campaign", "subscriber", "status", "created_at")