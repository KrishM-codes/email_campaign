import logging
from threading import Thread

from campaigns.services.email_service import process_email_job

logger = logging.getLogger(__name__)

class Worker(Thread):
    """
    Worker thread: consumes jobs (campaign_id, subscriber_id) from queue
    and processes them using process_email_job.
    """
    def __init__(self, q, retries):
        super().__init__(daemon=True)
        self.q = q
        self.retries = retries
    
    def run(self):
        while True:
            job = self.q.get()
            if job is None:
                self.q.task_done()
                break

            campaign_id, subscriber_id = job
            process_email_job(campaign_id, subscriber_id, self.retries)
            self.q.task_done()