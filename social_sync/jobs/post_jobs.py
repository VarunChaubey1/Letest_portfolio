from services.instagram import (
    save_instagram_posts,
    save_instagram_post_history
)

def instagram_post_discovery_job():

    print("Instagram Post Discovery Started")

    save_instagram_posts()

    print("Instagram Post Discovery Completed")


def instagram_insight_job():

    print("Instagram Insight Refresh Started")

    save_instagram_post_history()

    print("Instagram Insight Refresh Completed")

    