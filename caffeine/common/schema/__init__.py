from pydantic import ConstrainedStr


class PasswordStr(ConstrainedStr):
    min_length = 5
