import schedule
import time
from Skills.internet_access import InternetAccessSkill

class Scheduler:
    def __init__(self):
        # Initialize the InternetAccessSkill
        self.internet_access = InternetAccessSkill()

    def autonomous_browsing(self):
        """Trigger the InternetAccessSkill to browse autonomously."""
        print("Starting autonomous browsing...")
        result = self.internet_access.handle("autonomous browsing", context={})
        print(result)

    def start(self):
        """Start the scheduler."""
        # Schedule the autonomous browsing task every 10 minutes
        schedule.every(10).minutes.do(self.autonomous_browsing)

        # Run the scheduler in a loop
        print("Scheduler started. Autonomous browsing will run every 10 minutes.")
        while True:
            schedule.run_pending()
            time.sleep(1)