import logging
import time
from django.conf import settings
from campaigns.models import Campaign, Subscriber, SentEmail
from campaigns.utils import render_campaign_email,send_email

logger = logging.getLogger(__name__)

def process_email_job(campaign_id, subscriber_id, retries=2):
    status = "failed"
    response = ""

    try:
        campaign = Campaign.objects.get(id=campaign_id)
        subscriber = Subscriber.objects.get(id=subscriber_id)

        if not subscriber.is_active:
            return log_sent_email(campaign_id, subscriber_id, "failed", "inactive-subscriber")

        html, text = render_campaign_email(campaign, subscriber)

        attempts = retries + 1
        for attempt in range(1, attempts+1):
            result = send_email(
                from_email=settings.FROM_EMAIL,
                to_email=subscriber.email,
                subject=campaign.subject,
                html=html,
                text=text
            )
            if result["status"] == "success":
                return log_sent_email(
                    campaign_id, subscriber_id, "sent",
                    "dry-run" if result["dry_run"] else "ok"
                )
            
            # if the attempt failed,
            # we will retry after waiting for "attempt" seconds
            # this is a simple backoff algorithm
            time.sleep(attempt)
            response = result.get("error", "unknown-error")
        
        # all attempts failed
        return log_sent_email(campaign_id, subscriber_id, "failed", response)

    except Campaign.DoesNotExist:
        return log_sent_email(campaign_id, subscriber_id, "failed", "campaign-not-found")
    except Subscriber.DoesNotExist:
        return log_sent_email(campaign_id, subscriber_id, "failed", "subscriber-not-found")
    except Exception as e:
        logger.exception("Unexpected error while sending email")
        return log_sent_email(campaign_id,subscriber_id,"failed",f"Unexpected error: {e}")

def log_sent_email(campaign_id, subscriber_id, status, response):
    try:
        SentEmail.objects.create(
            campaign_id=campaign_id,
            subscriber_id=subscriber_id,
            status=status,
            response=response
        )
    except Exception as e:
        logger.error(f"Could not log SentEmail for campaign: %s", e)
    return {"status": status, "response": response}