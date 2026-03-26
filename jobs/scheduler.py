from apscheduler.schedulers.blocking import BlockingScheduler
import requests

def trigger_etl():
    """Triggers the API endpoint for ETL."""
    print("--- Starting Scheduled Job ---")
    try:
        response = requests.post("http://localhost:8000/run-etl", timeout=60)
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Connection error: {e}")

scheduler = BlockingScheduler()
scheduler.add_job(trigger_etl, 'interval', hours=12)

if __name__ == "__main__":
    print("Scheduler active. Press Ctrl+C to exit.")
    scheduler.start()