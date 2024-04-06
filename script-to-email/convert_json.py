import datetime
import os
import json
import string
import random
import sys

import yaml
from dateutil.parser import parse

emails = []

for filename in os.listdir('/app/input'):
    if filename.endswith('.json'):
        with open(os.path.join('/app/input', filename), 'r') as file:
            emails.append(json.load(file))

threads = {}
thread_id_map = {}
current_thread = []
characters = {}
for email in emails:
    from_ = email['from'] if 'from' in email else email['from_']
    if from_ not in characters:
        characters[from_] = {
            'name_and_email': email['from'] if 'from' in email else email[
                'from_']
        }
    for to in email['to']:
        if to not in characters:
            characters[to] = {'name_and_email': to}

    for cc in email['cc']:
        if cc not in characters:
            characters[cc] = {'name_and_email': cc}

    for bcc in email['bcc']:
        if bcc not in characters:
            characters[bcc] = {'name_and_email': bcc}

    if 'in_reply_to' in email and email['in_reply_to'] and email[
        'in_reply_to'] in thread_id_map:
        thread_id = thread_id_map[email['in_reply_to']]
        threads[thread_id].append(email)
        thread_id_map[email['id']] = thread_id
    else:
        thread_id = ''.join(random.choice(string.ascii_letters + string.digits)
                            for i in range(6))
        thread_id_map[email['id']] = thread_id
        threads[thread_id] = [email]


def get_id(email_):
    name_, _ = email_.split('<')
    name_ = name_.strip()
    return name_.lower().replace(' ', '_')


doc_parties = {}
for character in characters:
    name, email = character.split('<')
    email = email[:-1]
    name = name.strip()
    id_ = get_id(character)
    doc_parties[id_] = {
        'name': name,
        'email': email
    }

doc = {
    'threads': []
}

def sort_by_date(email_date):
    date_string = email_date["date"]
    date = parse(date_string)
    return date

last_hour_by_date = {}
def get_next_hour(date: str) -> str:
    if date in last_hour_by_date:
        last_hour_by_date[date] += 1
    else:
        last_hour_by_date[date] = random.randint(10, 18)

    return last_hour_by_date[date]

for thread_id in threads:
    thread = threads[thread_id]
    if not thread:
        continue

    doc_thread = {'subject': thread[0]['subject'], 'messages': []}
    sorted_thread = list(reversed(sorted(thread, key=sort_by_date)))

    newest_email, other_emails = sorted_thread[0], sorted_thread[1:]
    doc_message = {
        'from': get_id(
            newest_email['from_'] if 'from_' in newest_email else newest_email[
                'from']),
        'to': get_id(newest_email['to'][0]),
        'date': f"{newest_email['date']} "
                f"{get_next_hour(newest_email['date'])}:"
                f"{random.randint(0, 59)}",
        'message': newest_email['body'],
        'embedded_messages': []
    }
    for email in reversed(other_emails):
        doc_message['embedded_messages'].append({
            'from': get_id(email['from_'] if 'from_' in email else email[
                'from']),
            'date': f"{email['date']} "
                    f"{get_next_hour(email['date'])}:"
                    f"{random.randint(0, 59)}",
            'message': email['body']
        })

    if not doc_message['embedded_messages']:
        del doc_message['embedded_messages']

    doc_thread['messages'].append(doc_message)
    doc['threads'].append(doc_thread)

doc['parties'] = doc_parties
doc['settings'] = {'messy': True, 'html': True}

with open('/app/output/emails.yml', 'w') as f:
    f.write(yaml.dump(doc))
