import requests

from config import (
    GRAPH_VERSION,
    FB_PAGE_ID,
    META_ACCESS_TOKEN
)

from database import (
    get_connection,
    release_connection
)

BASE_URL = f"https://graph.facebook.com/{GRAPH_VERSION}"


# ==========================================
# GET FACEBOOK PROFILE INSIGHTS
# ==========================================

def get_facebook_profile_insights():

    metrics = [
        "page_post_engagements",
        "page_views_total",
        "page_video_views",
        "page_total_media_view_unique"
    ]

    url = (
        f"{BASE_URL}/{FB_PAGE_ID}/insights"
        f"?metric={','.join(metrics)}"
        f"&period=day"
        f"&access_token={META_ACCESS_TOKEN}"
    )

    response = requests.get(url)

    response.raise_for_status()

    data = response.json()

    result = {
        "reach": 0,
        "engagement": 0,
        "profile_views": 0,
        "video_views": 0
    }

    for item in data.get("data", []):

        name = item.get("name")

        value = (
            item.get("values", [{}])[-1]
            .get("value", 0)
        )

        if name == "page_total_media_view_unique":
            result["reach"] = value

        elif name == "page_post_engagements":
            result["engagement"] = value

        elif name == "page_views_total":
            result["profile_views"] = value

        elif name == "page_video_views":
            result["video_views"] = value

    return result



# ==========================================
# GET FACEBOOK PROFILE
# ==========================================

def get_facebook_profile():

    url = (
        f"{BASE_URL}/{FB_PAGE_ID}"
        f"?fields=name,fan_count"
        f"&access_token={META_ACCESS_TOKEN}"
    )

    response = requests.get(url)

    response.raise_for_status()

    return response.json()


def save_facebook_profile():

    profile = get_facebook_profile()

    insights = get_facebook_profile_insights()

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO facebook_profile (

            snapshot_date,
            page_id,
            page_name,
            fan_count,
            reach,
            engagement,
            profile_views,
            video_views,
            updated_at

        )
        VALUES (

            CURRENT_DATE,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            NOW()

        )

        ON CONFLICT(snapshot_date)

        DO UPDATE SET

            page_name = EXCLUDED.page_name,
            fan_count = EXCLUDED.fan_count,
            reach = EXCLUDED.reach,
            engagement = EXCLUDED.engagement,
            profile_views = EXCLUDED.profile_views,
            video_views = EXCLUDED.video_views,
            updated_at = NOW();
        """,
        (
            FB_PAGE_ID,
            profile.get("name"),
            profile.get("fan_count"),
            insights.get("reach"),
            insights.get("engagement"),
            insights.get("profile_views"),
            insights.get("video_views")
        )
    )

    conn.commit()

    cur.close()
    release_connection(conn)

    print("Facebook Profile Synced")

    return profile

# ==========================================
# GET FACEBOOK POSTS
# ==========================================

def get_facebook_posts():

    fields = [
        "id",
        "message",
        "created_time",
        "permalink_url",
        "full_picture",
        "attachments{media_type,url}"
    ]

    url = (
        f"{BASE_URL}/{FB_PAGE_ID}/posts"
        f"?fields={','.join(fields)}"
        f"&limit=100"
        f"&access_token={META_ACCESS_TOKEN}"
    )

    all_posts = []

    while url:

        response = requests.get(url)

        response.raise_for_status()

        data = response.json()

        all_posts.extend(data.get("data", []))

        url = data.get("paging", {}).get("next")

    return all_posts

# ==========================================
# SAVE FACEBOOK POSTS
# ==========================================

def save_facebook_posts():

    posts = get_facebook_posts()

    conn = get_connection()
    cur = conn.cursor()

    for post in posts:

        attachments = post.get("attachments", {}).get("data", [{}])
        media_type = attachments[0].get("media_type", "unknown") if attachments else "unknown"

        cur.execute(
            """
            INSERT INTO facebook_posts (
                post_id,
                message,
                permalink,
                media_url,
                post_created_time,
                last_media_refresh,
                updated_at,
                media_type
            )
            
            VALUES (
                %s,
                %s,
                %s,
                %s,
                %s,
                NOW(),
                NOW(),
                %s
            )
            ON CONFLICT(post_id)
            DO UPDATE SET
                message = EXCLUDED.message,
                permalink = EXCLUDED.permalink,
                media_url = EXCLUDED.media_url,
                media_type = EXCLUDED.media_type,
                last_media_refresh = NOW(),
                updated_at = NOW();
            """,
            (
                post.get("id"),
                post.get("message"),
                post.get("permalink_url"),
                post.get("full_picture"),
                post.get("created_time"),
                media_type
            )
        )

    conn.commit()

    cur.close()
    release_connection(conn)

    print(f"Facebook Posts Synced : {len(posts)}")

    return len(posts)

def get_facebook_post_insights(post_id):

    try:

        insight_url = (
            f"{BASE_URL}/{post_id}"
            f"?fields=shares,"
            f"comments.summary(true),"
            f"reactions.summary(true)"
            f"&access_token={META_ACCESS_TOKEN}"
        )

        response = requests.get(insight_url)

        response.raise_for_status()

        data = response.json()

        likes = (
            data.get("reactions", {})
            .get("summary", {})
            .get("total_count", 0)
        )

        comments = (
            data.get("comments", {})
            .get("summary", {})
            .get("total_count", 0)
        )

        shares = (
            data.get("shares", {})
            .get("count", 0)
        )

        reach = None
        impressions = None
        video_views = 0
        avg_watch_time = 0
        video_view_time = 0

        try:

            post_insight_url = (
                f"{BASE_URL}/{post_id}/insights"
                f"?metric=post_total_media_view_unique,post_media_view"
                f"&access_token={META_ACCESS_TOKEN}"
            )

            post_insight_response = requests.get(post_insight_url)

            if post_insight_response.status_code == 200:

                post_insight_data = post_insight_response.json()

                for item in post_insight_data.get("data", []):

                    if item.get("period") != "lifetime":
                        continue

                    value = (
                        item.get("values", [{}])[0]
                        .get("value", 0)
                    )

                    if item.get("name") == "post_total_media_view_unique":
                        reach = value

                    elif item.get("name") == "post_media_view":
                        impressions = value

        except Exception as e:

            print(f"Post Reach/Impression Error : {post_id}")
            print(str(e))

        try:

            video_url = (
                f"{BASE_URL}/{post_id}/insights"
                f"?metric=post_video_views"
                f"&access_token={META_ACCESS_TOKEN}"
            )

            video_response = requests.get(video_url)

            if video_response.status_code == 200:

                video_data = video_response.json()

                for item in video_data.get("data", []):

                    if (
                        item.get("name") == "post_video_views"
                        and item.get("period") == "lifetime"
                    ):

                        video_views = (
                            item.get("values", [{}])[0]
                            .get("value", 0)
                        )
                #AVG Watch TIME

            avg_url = (
                f"{BASE_URL}/{post_id}/insights"
                f"?metric=post_video_avg_time_watched"
                f"&access_token={META_ACCESS_TOKEN}"
            )

            avg_response = requests.get(avg_url)

            if avg_response.status_code == 200:

                avg_data = avg_response.json()

                for item in avg_data.get("data", []):

                    if (
                        item.get("name")
                        == "post_video_avg_time_watched"
                        and item.get("period") == "lifetime"
                    ):

                        avg_watch_time = (
                            item.get("values", [{}])[0]
                            .get("value", 0)
            )
                        
            # Video View Time

            time_url = (
                f"{BASE_URL}/{post_id}/insights"
                f"?metric=post_video_view_time"
                f"&access_token={META_ACCESS_TOKEN}"
            )

            time_response = requests.get(time_url)

            if time_response.status_code == 200:

                time_data = time_response.json()

                for item in time_data.get("data", []):

                    if (
                        item.get("name")
                        == "post_video_view_time"
                        and item.get("period") == "lifetime"
                    ):

                        video_view_time = (
                            item.get("values", [{}])[0]
                            .get("value", 0)
                        )            
        except Exception as e:

            print(
                f"Video Metrics Error : {post_id}"
            )

            print(str(e))

        return {
            "reach": reach,
            "impressions": impressions,

            "likes": likes,
            "comments": comments,
            "shares": shares,

            "engagement": (
                likes +
                comments +
                shares
            ),

            "video_views": video_views,
            "avg_watch_time": avg_watch_time,
            "video_view_time": video_view_time
        }

    except Exception as e:

        print(
            f"Facebook Insight Error : {post_id}"
        )

        print(str(e))

        return {
            "reach": None,
            "impressions": None,

            "likes": 0,
            "comments": 0,
            "shares": 0,

            "engagement": 0,

            "video_views": 0,
            "avg_watch_time": 0,
            "video_view_time": 0
        }

# ==========================================
# GET FACEBOOK REACH
# ==========================================

def get_facebook_page_reach():

    try:

        url = (
            f"{BASE_URL}/{FB_PAGE_ID}/insights"
            f"?metric=page_total_media_view_unique"
            f"&period=day"
            f"&access_token={META_ACCESS_TOKEN}"
        )

        response = requests.get(url)

        response.raise_for_status()

        data = response.json()

        return (
            data.get("data", [{}])[0]
            .get("values", [{}])[-1]
            .get("value", 0)
        )

    except Exception as e:

        print("Facebook Reach Error")
        print(str(e))

        return 0

# ==========================================
# SAVE FACEBOOK HISTORY
# ==========================================

def save_facebook_post_history(days=20):

    conn = get_connection()
    cur = conn.cursor()

    if days is None:

        cur.execute(
            """
            SELECT post_id
            FROM facebook_posts
            """
        )

    else:

        cur.execute(
            """
            SELECT post_id
            FROM facebook_posts
            WHERE post_created_time >=
            NOW() - (%s * INTERVAL '1 DAY')
            """,
            (days,)
        )

    posts = cur.fetchall()

    processed = 0

    for row in posts:

        post_id = row[0]

        insight = get_facebook_post_insights(
            post_id
        )

        if not insight:
            continue

        cur.execute(
    """
    UPDATE facebook_post_history
    SET
        snapshot_time = NOW(),
        reach = %s,
        impressions = %s,
        likes = %s,
        comments = %s,
        shares = %s,
        engagement = %s,
        video_views = %s,
        avg_watch_time = %s,
        video_view_time = %s
    WHERE post_id = %s
      AND snapshot_time::date = CURRENT_DATE
    """,
    (
        insight["reach"],
        insight["impressions"],

        insight["likes"],
        insight["comments"],
        insight["shares"],

        insight["engagement"],

        insight["video_views"],
        insight["avg_watch_time"],
        insight["video_view_time"],
        post_id
    )
)

        if cur.rowcount == 0:

            cur.execute(
        """
        INSERT INTO facebook_post_history (

            post_id,
            snapshot_time,

            reach,
            impressions,

            likes,
            comments,
            shares,

            engagement,

            video_views,
            avg_watch_time,
            video_view_time

        )

        VALUES (

            %s,
            NOW(),

            %s,
            %s,

            %s,
            %s,
            %s,

            %s,

            %s,
            %s,
            %s
        )
        """,
        (
            post_id,

            insight["reach"],
            insight["impressions"],

            insight["likes"],
            insight["comments"],
            insight["shares"],

            insight["engagement"],

            insight["video_views"],
            insight["avg_watch_time"],
            insight["video_view_time"]
        )
    )

        processed += 1

    conn.commit()

    cur.close()

    release_connection(conn)

    print(
        f"Facebook Insights Saved : {processed}"
    )

    return processed

