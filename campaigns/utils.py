import logging
from django.template.loader import render_to_string
from django.conf import settings

logger = logging.getLogger(__name__)

def render_campaign_email(campaign, subscriber):
    """Render HTML & plain text for a campaign email to a subscriber."""
    context = {
        "campaign": campaign,
        "subscriber": subscriber,
        "subject": campaign.subject,
        "unsubscribe_url": f"http://localhost:8000/api/unsubscribe/",
    }
    html = render_to_string("emails/campaign_email.html", context)
    text = campaign.plain_text_content
    return html, text


def send_email(from_email, to_email, subject, html, text):
    """Send email using SMTP or dry-run mode."""
    if settings.EMAIL_DRY_RUN:
        logger.info(f"[DRY RUN] Email to {to_email} with subject '{subject}'")
        return {"status": "success", "dry_run": True}
    pass
