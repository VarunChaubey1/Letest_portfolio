from apscheduler.schedulers.blocking import BlockingScheduler

from jobs.profile_jobs import (
    instagram_profile_job
)

from jobs.post_jobs import (
    instagram_post_discovery_job,
    instagram_insight_job
)

from services.facebook import (
    save_facebook_profile,
    save_facebook_posts,
    save_facebook_post_history
)



scheduler = BlockingScheduler()

# Instagram
scheduler.add_job(
    instagram_profile_job,
    "interval",
    minutes=1
)

scheduler.add_job(
    instagram_post_discovery_job,
    "interval",
    minutes=1
)

scheduler.add_job(
    instagram_insight_job,
    "interval",
    minutes=1
)

# Facebook
scheduler.add_job(
    save_facebook_profile,
    "interval",
    minutes=1
)

scheduler.add_job(
    save_facebook_posts,
    "interval",
    minutes=1
)

scheduler.add_job(
    save_facebook_post_history,
    "interval",
    minutes=1
)


print("Scheduler Started")

scheduler.start()