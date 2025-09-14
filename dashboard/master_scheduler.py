from apscheduler.schedulers.blocking import BlockingScheduler
import subprocess


scheduler = BlockingScheduler()

# --- Daily Job ---
@scheduler.scheduled_job("cron", hour=9, minute=0)  # runs every day at 9 AM
def run_daily():
    print("🚀 Running daily scheduler...")
    subprocess.run(["python", "scheduler.py"])  # execute your daily script

# --- Weekly Job ---
@scheduler.scheduled_job("cron", day_of_week="mon", hour=9, minute=0)  # runs every Monday at 9 AM
def run_weekly():
    print("📊 Running weekly scheduler...")
    subprocess.run(["python", "weekly_scheduler.py"])  # execute your weekly script

# Start scheduler
if __name__ == "__main__":
    print("✅ Master Scheduler started. Waiting for jobs...")
    scheduler.start()
