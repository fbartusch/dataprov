from typing import Optional


def ostr(string: Optional[str]) -> str:
    return str(string) if string else ""


def ostr_(string: Optional[str]) -> str:
    return str(string) + " " if string else ""
