import os
from queue import Queue
from datetime import date

from django.core.management.base import BaseCommand
from django.conf import settings

from campaigns.models import Campaign, Subscriber
from campaigns.services.worker import Worker

class Command(BaseCommand):
    help = "Send daily email campaigns to subscribers using pub-sub queue and worker threads."

    def add_arguments(self, parser):
        parser.add_argument(
            "--date",
            type=str,
            help="YYYY-MM-DD to send campaign for a specific date (default: today)",
        )

    def handle(self, *args, **options):
        # get date
        if options.get("date"):
            y,m,d = [int(x) for x in options["date"].split("-")]
            target_date = date(y,m,d)
        else:
            target_date = date.today()
        
        campaigns = Campaign.objects.filter(published_date=target_date)
        subscribers = Subscriber.objects.filter(is_active=True)

        if not campaigns.exists():
            self.stdout.write(self.style.WARNING(f"No campaigns found for {target_date}"))
            return
        if not subscribers.exists():
            self.stdout.write(self.style.WARNING("No active subscribers found"))
            return
        
        worker_count = settings.EMAIL_WORKER_COUNT or 8
        retries = settings.EMAIL_SEND_RETRIES or 2

        q = Queue()

        self.stdout.write(
            f"Dispatching {campaigns.count()} campaign(s) to {subscribers.count()} subscriber(s) "
            f"with {worker_count} worker(s), retries={retries}."
        )

        workers = [Worker(q, retries) for _ in range(worker_count)]
        for w in workers:
            w.start()
        
        total_jobs = 0
        for c in campaigns:
            for s in subscribers.iterator():
                q.put((c.id, s.id))
                total_jobs += 1
        
        for _ in workers:
            q.put(None)
        
        q.join()
        self.stdout.write(self.style.SUCCESS(f"All jobs processed: {total_jobs}"))