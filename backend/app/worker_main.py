"""Worker entrypoint — starts APScheduler and runs the fetch/classify/dedup pipeline."""

import asyncio
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s %(message)s")
logger = logging.getLogger("headlines.worker")


async def main():
    from app.workers.scheduler import start_scheduler

    scheduler = await start_scheduler()
    logger.info("Worker started. Scheduler running.")
    try:
        while True:
            await asyncio.sleep(60)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
        logger.info("Worker shut down.")


if __name__ == "__main__":
    asyncio.run(main())
