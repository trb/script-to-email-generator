import datetime
import os
import string
from email.message import EmailMessage
import random
from typing import List

from .thread import Thread
from .dates import IncrementalDateGenerator
from .message import Message, EmbeddedMessage

from .script import Script

DATE_FORMAT = "%a, %b %d, %Y at %I:%M %p"


def random_string(n):
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=n))


def messy_headers():
    return {
        "Received": "by 2002:a17:90b:34c:0:0:0:0 with SMTP id "
                    "fh12csp241259pjb; {} ("
                    "PST)".format(datetime.datetime.now().strftime("%a, " "%d %b %Y " "%H:%M:%S")),
        "X-Google-Smtp-Source": random_string(76),
        "ARC-Seal": "i=1; a=rsa-sha256; t={}; cv=none;"
                    "d=google.com; s=arc-20160816;"
                    "b={}==".format(random.randint(1000000, 10000000),
                                    random_string(128)),
        "ARC-Message-Signature": "i=1; a=rsa-sha256; c=relaxed/relaxed; d=google.com; s=arc-20160816;"
                                 "h=mime-version:subject:references:in-reply-to:message-id:to:from:date"
                                 ":dkim-signature;"
                                 "bh={}=;"
                                 "b={}==".format(random_string(20),
                                                 random_string(256)),
        "X-Mailer": "WebService/1.1.19797 YMailNorrin",
        "X-IncomingTopHeaderMarker": "OriginalChecksum:844D73727AE689FF3C9272E149DC8A162DE0376CF0450AEBD1E8B6C80A0D789C;UpperCasedChecksum:E6AB3BB83FE007AB4197C0B8D593F8E753D5CA210CB25CF09BEBFB337F586FB4;SizeAsReceived:6543;Count:41",
        "DKIM-Signature": "v=1; a=rsa-sha256; c=relaxed/relaxed; d=hotmail.com;"
                          "s=selector1;"
                          "h=From:Date:Subject:Message-ID:Content-Type:MIME-Version:X-MS-Exchange-SenderADCheck;"
                          "bh={};"
                          "b={}".format(random_string(50), random_string(256)),
        "X-MS-Exchange-AntiSpam-MessageData-Original-0": random_string(512),
        "X-MS-Exchange-Transport-CrossTenantHeadersStamped": random_string(32),
        "X-MS-Exchange-Organization-ExpirationStartTime": datetime.datetime.now().isoformat(),
        "X-MS-Exchange-Organization-ExpirationStartTimeReason": "OriginalSubmit",
        "X-MS-Exchange-Organization-ExpirationInterval": "1:00:00:00.0000000",
        "X-MS-Exchange-Organization-ExpirationIntervalReason": "OriginalSubmit",
        "X-MS-Exchange-Organization-Network-Message-Id": random_string(32),
        "X-Message-Info": random_string(50),
        "X-Message-Delivery": random_string(32),
        "X-Microsoft-Antispam-Message-Info": random_string(512),
        "X-MS-Exchange-CrossTenant-AuthAs": "Anonymous",
        "X-MS-Exchange-CrossTenant-FromEntityHeader": "Internet",
        "X-MS-Exchange-Transport-EndToEndLatency": "00:00:02.0401855",
    }


def replyify(message: EmbeddedMessage, date: datetime.datetime):
    first_line = " On {} {} wrote:".format(
        date.strftime(DATE_FORMAT),
        message.from_.email_address
    )

    lines = message.message.splitlines()
    lines = ["> {}".format(line) for line in lines]

    lines.insert(0, first_line)

    return lines


def indent(lines: List[str], indentation=""):
    lines = ["{}{}".format(indentation, line) for line in lines]
    indentation += ">"
    return lines, indentation


def make_text_content(message: Message, start_date: datetime.datetime):
    date_generator = IncrementalDateGenerator(start_date)

    embedded_messages = []
    for embedded_message in message.embedded_messages:
        embedded_messages.append(
            replyify(embedded_message,
                     date_generator.next(embedded_message.date))
        )

    formatted_messages = []
    indentation = ""
    for embedded_message_lines in reversed(embedded_messages):
        lines, indentation = indent(embedded_message_lines, indentation)
        formatted_messages.append(lines)

    embedded_messages_text = "\n\n".join(
        ["\n".join(message_lines) for message_lines in formatted_messages]
    )

    return (
        "{}\n\n{}".format(message.message, embedded_messages_text),
        date_generator.date,
    )


def make_html_content(
        message: Message, start_date: datetime.datetime, messy: bool = False
):
    date_generator = IncrementalDateGenerator(start_date)

    if messy:
        p = '<p style="white-space: pre; text-align: left, font-family: sans; font-size: 14px; background-color: inherit; cursor: inherit">{}</p>'
        div = (
            '<div style="border-left: 3px grey solid; padding-left: 5px; '
            "font-size: 14px; font-weight: normal; display: block; cursor: "
            "inherit; background-position: center"
            '">{}</div>'
        )
    else:
        p = "<p>{}</p>"
        div = '<div style="border-left: 3px grey solid; padding-left: 5px">{}</div>'

    html_messages = []
    for embedded_message in message.embedded_messages:
        html = "On {} {} wrote:<br />".format(
            date_generator.next(embedded_message.date).strftime(
                "%a, %b %d, %Y at %I:%M %p"
            ),
            embedded_message.from_.email_address
        )
        html = p.format(html)
        html += embedded_message.html
        html_messages.append(html)

    wrapper = div
    wrapped_messages = []
    for embedded_message in reversed(html_messages):
        wrapped_messages.append(wrapper.format(embedded_message))
        wrapper = div.format(wrapper)

    html_body = "".join([message.html,
                         "<br /><br />"] + wrapped_messages)
    return '<div style="width: 520px;">{}</div>'.format(html_body), start_date

class Generator:
    def __init__(self, script: Script):
        self.script = script

    def generate_thread(self, thread: Thread):
        first_message = thread.messages[0]
        if first_message.embedded_messages:
            first_message = first_message.embedded_messages[0]

        emails = []
        date_generator = IncrementalDateGenerator(first_message.date or None)

        if thread.subject:
            subject = thread.subject
        else:
            subject = "No subject"

        message_ids = []
        last_message_id = None

        for message in thread.messages:
            email = EmailMessage()

            message_id = '<{}@infra1.email.app.goodfact.co>'.format(
                random_string(48)).upper()

            email['Message-ID'] = message_id
            if message_ids:
                email['References'] = ','.join(message_ids)
            if last_message_id:
                email['In-Reply-To'] = last_message_id
            message_ids.append(message_id)
            last_message_id = message_id

            if message.subject:
                email["Subject"] = subject
                subject = "RE: {}".format(subject)
            else:
                email["Subject"] = subject
                if not subject.startswith("RE:"):
                    subject = "RE: {}".format(subject)

            if message.from_:
                email["From"] = message.from_.email_address
            if message.to:
                email["To"] = ", ".join([party.email_address for party in
                                         message.to])

            if message.embedded_messages:
                message_text, new_date = make_text_content(message,
                                                           date_generator.date)
                message_html, _ = make_html_content(
                    message, date_generator.date, self.script.settings.messy
                )
                date_generator.set_date(new_date)
            else:
                message_text = message.message
                message_html = message.html

            if self.script.settings.html:
                email.make_alternative()
                email.add_alternative(message_text)
                email.add_alternative(message_html, subtype="html")
            else:
                email.set_content(message_text)

            email["Date"] = date_generator.next(message.date)

            if message.attachments:
                for attachment in message.attachments:
                    with open(attachment.file, "rb") as attachment_file:
                        email.add_attachment(
                            attachment_file.read(),
                            filename=os.path.basename(attachment.file),
                            maintype=attachment.maintype,
                            subtype=attachment.subtype,
                        )

            if self.script.settings.messy:
                headers = messy_headers()
                for header in headers:
                    email[header] = headers[header]

            emails.append(email)

        return emails

    def generate_emails(self):
        emails = []
        for thread in self.script.threads:
            emails.extend(self.generate_thread(thread))
        return emails
