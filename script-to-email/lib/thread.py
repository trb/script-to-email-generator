from typing import List

from .message import Message
from .party import Party


class Thread:
    def __init__(
        self,
        messages: List[Message],
        subject: str = "",
        date: any = "",
        bcc: List[Party] = None,
        cc: List[Party] = None,
        to: List[Party] = None,
        from_: Party = None,
    ):
        self.messages = messages
        self.subject = subject
        self.date = date
        if bcc is None:
            bcc = []
        if cc is None:
            cc = []
        if to is None:
            to = []
        self.from_ = from_
        self.to = to
        self.cc = cc
        self.bcc = bcc
