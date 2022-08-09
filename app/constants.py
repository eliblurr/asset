SORT_STR_X = r'^-'
SORT_STR = r'(^-)?\w'
DT_Y = r'^(lt|lte|gt|gte)'
PHONE = r'^\+?1?\d{9,15}$'
Q_STR_X = r'^[\w]+:[\w]+$'
Q_X = '^[\w]+$|{cols}:[\w]+$'
DT_Z = r'^((lt|lte|gt|gte):)?(\d\d\d\d)$'
EMAIL = r'^[\w\-\.]+@([\w\-]+\.)+[\w\-]{2,4}$'
COLOR_HEX = r'^#([a-fA-F0-9]{6}|[a-fA-F0-9]{3})$'
SUPPORTED_EXT = [".csv", ".CSV", ".xlsx", ".xlsm", ".xls", ".xml", ".xla"]
DT_X = r'^((lt|lte|gt|gte):)?\d\d\d\d-(0?[1-9]|1[0-2])-(0?[1-9]|[12][0-9]|3[01]) (00|[0-9]|1[0-9]|2[0-3]):([0-9]|[0-5][0-9]):([0-9]|[0-5][0-9])?'
URL = r'(https|http)?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)'
MONTHS = {'january':1, 'february':2, 'march':3, 'april':4, 'may':5, 'june':6, 'july':7, 'august':8, 'september':9, 'october':10, 'november':11, 'december':12}
OPS = ['view', 'detail', 'report', 'disable', 'delete', 'edit', 'add', 'assign', 'cancel', 'deliver', 'buy', 'ready', 'end', 'verify', 'issue']

# SORT_STR = r'(^-)?\w'
# SORT_STR_X = r'^-'
# Q_STR = r'^[\w]+$'
# Q_STR_X = r'^[\w]+:[\w]+$'
# DT = r'^\d\d\d\d-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01]) (00|[0-9]|1[0-9]|2[0-3]):([0-9]|[0-5][0-9]):([0-9]|[0-5][0-9])$'
# OPS = {'lt':'<', 'gt':'>', 'lte':'<=', 'gte':'>='}
# PHONE = r'^\+?1?\d{9,15}$'
# EMAIL = r'^[\w\-\.]+@([\w\-]+\.)+[\w\-]{2,4}$'