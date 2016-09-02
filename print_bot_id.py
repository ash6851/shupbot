# xoxb-75533350692-FAXaRJwjyN0eXXLBT27pNlcB
import os
from slackclient import SlackClient

BOT_NAME = 'shupbot'

slack_client = SlackClient(os.environ.get('SLACKBOT_API_TOKEN'))

if __name__ == "__main__":
    api_call = slack_client.api_call("users.list")
    if api_call.get('ok'):
        print(api_call)
        # retrieve all users so we can find our bot
        users = api_call.get('members')
        for user in users:
            if 'name' in user and user.get('name') == BOT_NAME:
                print("Bot ID for '" + user['name'] + "' is " + user.get('id'))
else:
    print("could not find bot user with the name " + BOT_NAME)
