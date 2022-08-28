from __future__ import annotations
from typing import List

from .party import Party


class Attachment:
    def __init__(self, mimetype: str = None, file=None):
        if not file:
            raise Exception("Attachments require a file")

        mimetype = mimetype.split("/")
        self.maintype = mimetype[0]
        self.subtype = mimetype[1]
        self.file = file


class BaseMessage:
    def __init__(self, from_, message, messy):
        self.from_ = from_
        self._message = message
        self.messy = messy

        if self.messy:
            self.p = (
                '<p data-attr-gen="invalid"; style="display: block; '
                "white-space: pre; text-align: left; font-size: 14px; "
                "font-weight: inherit"
                '">{}</p>'
            )
            self.span = (
                '<span data-attr-gen="processed"; style="display: '
                "inline; "
                "white-space: pre; text-align: left; font-size: 12px; "
                "font-weight: normal"
                '">{}</span>'
            )
        else:
            self.p = "<p>{}</p>"
            self.span = "<span>{}</span>"

    @property
    def message(self):
        if self.from_.signature:
            return "\n".join(
                [self._message, "--", "\n".join(self.from_.signature.split("\n"))]
            )
        return self._message

    @property
    def html(self):
        paragraphs = [self.p.format(part) for part in self._message.split("\n\n")]
        if self.from_.signature:
            signature = "<br />".join(
                [self.span.format(line) for line in self.from_.signature.splitlines()]
            )
            paragraphs.append("<br />")
            paragraphs.append(self.p.format(signature))
        return "\n".join(paragraphs)


# @todo make embedded messages work to generate a single-email thread
class EmbeddedMessage(BaseMessage):
    def __init__(
        self,
        from_: Party = None,
        date: str = None,
        message: str = None,
        messy: bool = False,
    ):
        super().__init__(from_, message, messy)
        self.date = date


class Message(BaseMessage):
    def __init__(
        self,
        from_: Party,
        to=None,
        cc=None,
        bcc=None,
        message: str = "",
        embedded_messages: List[EmbeddedMessage] = None,
        date: str = None,
        subject: str = "",
        attachments: List[Attachment] = None,
        messy: bool = False,
    ):
        super().__init__(from_, message, messy)
        self.date = date
        self.subject = subject
        self.to = to
        self.cc = cc
        self.bcc = bcc
        self.attachments = attachments
        self.embedded_messages = embedded_messages
