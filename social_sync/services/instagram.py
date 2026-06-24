import requests

from config import (
    GRAPH_VERSION,
    IG_ACCOUNT_ID,
    META_ACCESS_TOKEN
)

from database import (
    get_connection,
    release_connection
)

BASE_URL = f"https://graph.facebook.com/{GRAPH_VERSION}"


# ==========================================
# GET INSTAGRAM PROFILE
# ==========================================

def get_instagram_profile():

    fields = [
        "username",
        "name",
        "followers_count",
        "follows_count",
        "media_count"
    ]

    url = (
        f"{BASE_URL}/{IG_ACCOUNT_ID}"
        f"?fields={','.join(fields)}"
        f"&access_token={META_ACCESS_TOKEN}"
    )

    response = requests.get(url)

    response.raise_for_status()

    return response.json()

# ==========================================
# GET INSTAGRAM PROFILE INSIGHTS
# ==========================================

def get_instagram_profile_insights():

    result = {
        "reach": 0,
        "views": 0,
        "profile_views": 0,
        "accounts_engaged": 0
    }

    # Reach
    try:

        url = (
            f"{BASE_URL}/{IG_ACCOUNT_ID}/insights"
            f"?metric=reach"
            f"&period=day"
            f"&access_token={META_ACCESS_TOKEN}"
        )

        response = requests.get(url)

        if response.status_code == 200:

            data = response.json()

            result["reach"] = (
                data.get("data", [{}])[0]
                .get("values", [{}])[-1]
                .get("value", 0)
            )

    except Exception as e:

        print(f"Reach Error : {str(e)}")

    # Views, Profile Views, Accounts Engaged
    metrics = [
        "views",
        "profile_views",
        "accounts_engaged"
    ]

    for metric in metrics:

        try:

            url = (
                f"{BASE_URL}/{IG_ACCOUNT_ID}/insights"
                f"?metric={metric}"
                f"&metric_type=total_value"
                f"&period=day"
                f"&access_token={META_ACCESS_TOKEN}"
            )

            response = requests.get(url)

            if response.status_code != 200:
                continue

            data = response.json()

            result[metric] = (
                data.get("data", [{}])[0]
                .get("total_value", {})
                .get("value", 0)
            )

        except Exception as e:

            print(f"{metric} Error : {str(e)}")

    return result


# ==========================================
# SAVE PROFILE TO DATABASE
# ==========================================

def save_instagram_profile():

    profile = get_instagram_profile()

    insights = get_instagram_profile_insights()

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO instagram_profile (
            snapshot_date,
            username,
            full_name,
            followers_count,
            follows_count,
            media_count,
            reach,
            views,
            profile_views,
            accounts_engaged,
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
            %s,
            %s,
            NOW()
        )

        ON CONFLICT (snapshot_date)

        DO UPDATE SET

            username = EXCLUDED.username,
            full_name = EXCLUDED.full_name,
            followers_count = EXCLUDED.followers_count,
            follows_count = EXCLUDED.follows_count,
            media_count = EXCLUDED.media_count,
            reach = EXCLUDED.reach,
            views = EXCLUDED.views,
            profile_views = EXCLUDED.profile_views,
            accounts_engaged = EXCLUDED.accounts_engaged,
            updated_at = NOW();
        """,
                (
                profile.get("username"),
                profile.get("name"),
                profile.get("followers_count"),
                profile.get("follows_count"),
                profile.get("media_count"),
                insights.get("reach"),
                insights.get("views"),
                insights.get("profile_views"),
                insights.get("accounts_engaged")
            )
    )

    conn.commit()

    cur.close()
    release_connection(conn)

    print("Instagram Profile Synced")

    return profile


# ==========================================
# GET INSTAGRAM POSTS
# ==========================================

def get_instagram_posts():

    fields = [
    "id",
    "caption",
    "permalink",
    "media_url",
    "thumbnail_url",
    "media_type",
    "media_product_type",
    "timestamp",
    "like_count",
    "comments_count"
]

    url = (
        f"{BASE_URL}/{IG_ACCOUNT_ID}/media"
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
# SAVE POSTS TO DATABASE
# ==========================================

def save_instagram_posts():

    posts = get_instagram_posts()

    conn = get_connection()
    cur = conn.cursor()

    for post in posts:

        cur.execute(
            """
            INSERT INTO instagram_posts (

                media_id,
                caption,
                permalink,
                media_url,
                thumbnail_url,
                media_type,
                media_product_type,
                post_created_time,
                last_media_refresh,
                updated_at

            )
            VALUES (

                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                NOW(),
                NOW()

            )

            ON CONFLICT (media_id)

            DO UPDATE SET

                caption = EXCLUDED.caption,
                permalink = EXCLUDED.permalink,
                media_url = EXCLUDED.media_url,
                thumbnail_url = EXCLUDED.thumbnail_url,
                media_type = EXCLUDED.media_type,
                media_product_type = EXCLUDED.media_product_type,
                last_media_refresh = NOW(),
                updated_at = NOW();
            """,
            (
                post.get("id"),
                post.get("caption"),
                post.get("permalink"),
                post.get("media_url"),
                post.get("thumbnail_url"),
                post.get("media_type"),
                post.get("media_product_type"),
                post.get("timestamp")
            )
        )

    conn.commit()

    cur.close()
    release_connection(conn)

    print(f"Posts Synced : {len(posts)}")

    return len(posts)


# ==========================================
# TEST
# ==========================================

if __name__ == "__main__":

    save_instagram_profile()
    save_instagram_posts()

    # ==========================================
# GET INSIGHTS FOR ONE POST
# ==========================================

def get_media_insights(media_id, media_type):

    result = {
        "reach": 0,
        "impressions": 0,
        "views": 0,
        "likes": 0,
        "comments": 0,
        "shares": 0,
        "saved": 0,
        "total_interactions": 0
    }

    metrics = [
        "reach",
        "likes",
        "comments",
        "shares",
        "saved",
        "total_interactions",
        "views"
    ]

    url = (
        f"{BASE_URL}/{media_id}/insights"
        f"?metric={','.join(metrics)}"
        f"&access_token={META_ACCESS_TOKEN}"
    )

    response = requests.get(url)

    if response.status_code != 200:
        print(f"Instagram Insight Failed : {media_id}")
        try:

            fallback_url = (
                f"{BASE_URL}/{media_id}"
                f"?fields=like_count,comments_count"
                f"&access_token={META_ACCESS_TOKEN}"
            )

            fallback_response = requests.get(fallback_url)

            if fallback_response.status_code == 200:

                fallback_data = fallback_response.json()

                result["likes"] = fallback_data.get("like_count", 0)
                result["comments"] = fallback_data.get("comments_count", 0)
                result["total_interactions"] = (
                    result["likes"] +
                    result["comments"]
                )

        except Exception as e:

            print(f"Instagram Fallback Insight Error : {media_id}")
            print(str(e))

        return result

    data = response.json()

    for item in data.get("data", []):

        name = item.get("name")

        value = (
            item.get("values", [{}])[0]
            .get("value", 0)
        )

        result[name] = value

    result["impressions"] = result.get("views", 0)

    return result


# ==========================================
# SAVE INSIGHTS HISTORY
# ==========================================

def save_instagram_post_history(days=20):

    conn = get_connection()
    cur = conn.cursor()

    if days is None:

        cur.execute(
            """
            SELECT media_id,
                   media_type
            FROM instagram_posts
            """
        )

    else:

        cur.execute(
            """
            SELECT media_id,
                   media_type
            FROM instagram_posts
            WHERE post_created_time >=
            NOW() - (%s * INTERVAL '1 DAY')
            """,
            (days,)
        )

    posts = cur.fetchall()

    processed = 0

    for media_id, media_type in posts:

        insight = get_media_insights(
            media_id,
            media_type
        )

        if not insight:
            continue

        cur.execute(
            """
            UPDATE instagram_post_history
            SET
                snapshot_time = NOW(),
                reach = %s,
                impressions = %s,
                views = %s,
                likes = %s,
                comments = %s,
                shares = %s,
                saves = %s,
                engagement = %s
            WHERE media_id = %s
              AND snapshot_time::date = CURRENT_DATE
            """,
            (
                insight.get("reach", 0),
                insight.get("impressions", 0),
                insight.get("views", 0),
                insight.get("likes", 0),
                insight.get("comments", 0),
                insight.get("shares", 0),
                insight.get("saved", 0),
                insight.get("total_interactions", 0),
                media_id
            )
        )

        if cur.rowcount == 0:

            cur.execute(
                """
                INSERT INTO instagram_post_history (

                    media_id,
                    snapshot_time,

                    reach,
                    impressions,
                    views,

                    likes,
                    comments,
                    shares,
                    saves,

                    engagement

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

                    %s
                )
                """,
                (
                    media_id,

                    insight.get("reach", 0),
                    insight.get("impressions", 0),
                    insight.get("views", 0),

                    insight.get("likes", 0),
                    insight.get("comments", 0),
                    insight.get("shares", 0),
                    insight.get("saved", 0),

                    insight.get("total_interactions", 0)
                )
            )

        processed += 1

    conn.commit()

    cur.close()
    release_connection(conn)

    print(
        f"Instagram Insights Saved : {processed}"
    )
