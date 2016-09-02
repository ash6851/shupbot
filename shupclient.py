import os
import time
import random
import datetime
import json

import operator
from slackclient import SlackClient

# starterbot's ID as an environment variable
BOT_ID = os.environ.get("BOT_ID")

# constants
print BOT_ID
AT_BOT = "<@" + BOT_ID + ">"
EXAMPLE_COMMAND = "shup"

# instantiate Slack & Twilio clients
slack_client = SlackClient(os.environ.get('SLACKBOT_API_TOKEN'))

shup_records = {}

shup_responses = ['recorded', 'erhh merhh gherd']


def handle_command(command, channel, who, rec_file):
    response = 'shups!!!!!'
    keep_alive = True
    if command.startswith('shup'):
        number = command.split('shup')[1]
        try:
            shup_entry = int(number)
        except ValueError:
            response = 'Did not understand shup entry'
        else:
            if not shup_records.get(who):
                user_info = slack_client.api_call('users.info', user=who)
                first_name = user_info['user']['profile']['first_name']
                shup_records[who] = {
                    'name': first_name,
                    'shup_history': {}
                }

            shup_history = shup_records.get(who)['shup_history']
            today = datetime.date.today().strftime('%m/%d/%Y')
            count = shup_history.get(today, 0)
            shup_history[today] = count + shup_entry
            response = shup_responses[random.randint(0, len(shup_responses) - 1)]
    elif command.startswith('me'):
        shup_history = shup_records.get(who)['shup_history']
        response = 'YOU HAVE DONE NOTHING! 20 shups NOW!'
        if shup_records.get(who):
            if command.split('me')[1].strip().lower() == 'total':
                response = 'Your total shups: %s' % sum(shup_history.values())
            else:
                nice_hist = '\n'.join(['%s: %s' % (d, h) for d, h in shup_history.iteritems()])
                response = 'Your shups history: %s' % nice_hist
        # slack_client.api_call("chat.postMessage", channel=channel,
        #                       text=response, as_user=True)
    elif command.startswith('leaderboard'):
        totals = [(record['name'], sum(record['shup_history'].values())) for user, record in
                  shup_records.iteritems()]
        sorted_totals = sorted(totals, key=operator.itemgetter(1), reverse=True)
        hist = ['%s. %s with %s shups' % (i + 1, sorted_totals[i][0], sorted_totals[i][1])
                for i in range(0, len(sorted_totals))]
        response = '\n'.join(hist)
        # slack_client.api_call("chat.postMessage", channel=channel,
        #                       text=response, as_user=True)
    elif command.startswith('shutdown'):
        response = 'Goodbye.'
        keep_alive = False
    else:
        response = 'Commands:\n' \
                   'shup <number> to record your shups\n' \
                   'me to get your records\n' \
                   'Example: @shupbot shup 10'
    slack_client.api_call("chat.postMessage", channel=channel,
                          text=response, as_user=True)
    return keep_alive


def parse_slack_output(slack_rtm_output):
    """
        The Slack Real Time Messaging API is an events firehose.
        this parsing function returns None unless a message is
        directed at the Bot, based on its ID.
    """
    output_list = slack_rtm_output
    print(output_list)
    if output_list and len(output_list) > 0:
        for output in output_list:
            if output and 'text' in output and AT_BOT in output['text']:
                # return text after the @ mention, whitespace removed
                print(output['text'])
                return (output['text'].split(AT_BOT)[1].strip().lower(),
                        output['user'], output['channel'])
    return None, None, None


if __name__ == "__main__":
    READ_WEBSOCKET_DELAY = 1  # 1 second delay between reading from firehose
    if slack_client.rtm_connect():
        # rec_file = 'shup_records_{}.txt'.format(datetime.date.today(), '%Y-%m-%d')
        rec_file_name = 'shup_records.txt'
        with open(rec_file_name, mode='r') as rec_file:
            try:
                shup_records = json.load(rec_file)
            except ValueError:
                shup_records = {}

        with open(rec_file_name, mode='w+') as rec_file:
            print shup_records
            print("Shupbot connected and running!")
            while True:
                command, who, channel = parse_slack_output(slack_client.rtm_read())
                if command and channel:
                    keep_alive = handle_command(command, channel, who, rec_file)
                    if not keep_alive:
                        json.dump(shup_records, rec_file)
                        break
                time.sleep(READ_WEBSOCKET_DELAY)
    else:
        print("Connection failed. Invalid Slack token or bot ID?")
