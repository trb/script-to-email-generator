class Party:
    def __init__(self, name: str, email: str, signature: str = "", role: str = ""):
        self.name = name
        self.email = email
        self.role = role
        self.signature = signature

    @property
    def email_address(self):
        if self.name and self.email:
            return "{} <{}>".format(self.name, self.email)

        if self.email:
            return self.email

        if self.name:
            return self.name

        return ""
