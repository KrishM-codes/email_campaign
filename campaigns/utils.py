import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from django.conf import settings
from django.template.loader import render_to_string

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
    """Send email using SMTP (Mailgun) or dry-run mode."""
    if settings.EMAIL_DRY_RUN:
        logger.info(f"[DRY RUN] Email to %s with subject '%s'", to_email, subject)
        return {"status": "success", "dry_run": True}
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = from_email
        msg["To"] = to_email

        msg.attach(MIMEText(text, "plain"))
        msg.attach(MIMEText(html, "html"))

        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASS)
            server.sendmail(from_email, [to_email], msg.as_string())

        logger.info("Email sent to %s", to_email)
        return {"status": "success", "dry_run": False}

    except Exception as e:
        logger.error("Error sending email to %s: %s", to_email, str(e))
        return {"status": "failed", "error": str(e)}
