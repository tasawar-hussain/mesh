from settings import SLACK_TEST_USERS


def test_users():
    """
    Real slack users for testing
    """
    if SLACK_TEST_USERS and len(SLACK_TEST_USERS) > 1:
        return SLACK_TEST_USERS.split(",")
    return []


def mention_user(slack_user_id): return f"<@{slack_user_id}>"


def mention_users(users):
    """
    Converts the slack user ids to mention format string
    """
    result = list(map(mention_user, users))
    return ", ".join(result)


def message_text(users):
    mentions = mention_users(users)
    return f"""Are you ready to take a break?

    Hello {mentions},
    This is your friendly Mesh 👋, visiting to help you connect with your teammates. I have picked you from the #lets-meet slack channel to mesh.

    This is an opportunity for you to get to know each other if you don't already.

    Now that you're here, initiate a conversation and pick a time to meet for a ☕, 🍔, or 🍦 (or via 💻 if you're in different locations).

    Please follow SOPs to keep yourself & others safe if you decide to meet in person.

    Have Fun!
    """
