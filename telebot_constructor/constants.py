# for scoping stores, e.g. when used in a larger app
from multidict import istr

CONSTRUCTOR_PREFIX = "telebot-constructor"

CONSTRUCTOR_HEADER_PREFIX = "X-Telebot-Constructor"
FILENAME_HEADER = istr(f"{CONSTRUCTOR_HEADER_PREFIX}-Filename")
