from database import get_connection, release_connection
from services.facebook import (
    save_facebook_post_history,
    save_facebook_posts,
    save_facebook_profile,
)
from services.instagram import (
    save_instagram_post_history,
    save_instagram_posts,
    save_instagram_profile,
)


def clear_all_sync_data():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        TRUNCATE TABLE
            instagram_post_history,
            facebook_post_history,
            instagram_posts,
            facebook_posts,
            instagram_profile,
            facebook_profile
        RESTART IDENTITY CASCADE;
        """
    )

    conn.commit()
    cur.close()
    release_connection(conn)

    print("All sync tables cleared")


def run_full_rebuild():
    clear_all_sync_data()

    save_instagram_profile()
    save_instagram_posts()
    save_instagram_post_history(days=None)

    save_facebook_profile()
    save_facebook_posts()
    save_facebook_post_history(days=None)

    print("Full fresh rebuild completed")


if __name__ == "__main__":
    run_full_rebuild()
