import os.path

from .party import Party
from .message import Message, Attachment, EmbeddedMessage
from .thread import Thread
from .settings import Settings
from typing import List


class Script:
    def __init__(
        self,
        parties: dict[str, Party],
        threads: List[Thread],
        settings: Settings,
        path: str = None,
    ):
        self.parties = parties
        self.threads = threads
        self.settings = settings
        self.path = path

    @staticmethod
    def deserialize(data, path: str = None):
        if "settings" in data:
            settings = Settings(**data["settings"])
        else:
            settings = Settings()

        parties = {}
        for party in data["parties"]:
            parties[party] = Party(**data["parties"][party])

        threads = []
        for thread in data["threads"]:
            messages = []
            for message in thread["messages"]:
                message["from_"] = parties[message["from"]]

                for recipient_type in ["to", "cc", "bcc"]:
                    if recipient_type in message:
                        recipient = message[recipient_type]
                        if "," in recipient:
                            recipients = recipient.split(",")
                        else:
                            recipients = [recipient]
                        recipients = [parties[recipient] for recipient in recipients]
                        message[recipient_type] = recipients
                del message["from"]

                attachments = None
                if "attachments" in message and message["attachments"]:
                    attachments = []
                    for attachment in message["attachments"]:
                        if attachment["file"].startswith("/"):
                            attachment_path = attachment["file"]
                        else:
                            attachment_path = os.path.realpath(
                                os.path.join(os.path.dirname(path), attachment["file"])
                            )
                        attachments.append(
                            Attachment(mimetype=attachment["mimetype"], file=attachment_path)
                        )
                    del message["attachments"]

                embedded_messages = None
                if "embedded_messages" in message and message["embedded_messages"]:
                    embedded_messages = []
                    for embedded_message in message["embedded_messages"]:
                        embedded_message["from_"] = None
                        if "from" in embedded_message:
                            embedded_message["from_"] = parties[
                                embedded_message["from"]
                            ]
                        del embedded_message["from"]
                        embedded_messages.append(
                            EmbeddedMessage(messy=settings.messy, **embedded_message)
                        )
                    del message["embedded_messages"]

                messages.append(
                    Message(
                        embedded_messages=embedded_messages,
                        attachments=attachments,
                        messy=settings.messy,
                        **message
                    )
                )
            threads.append(Thread(messages=messages, subject=thread["subject"]))

        return Script(parties=parties, threads=threads, settings=settings, path=path)
