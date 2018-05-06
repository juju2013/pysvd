from enum import Enum

class access(Enum):
    read_only = 'read-only'
    write_only = 'write-only'
    read_write = 'read-write'
    write_once = 'writeOnce'
    read_write_once = 'read-writeOnce'

class enum_usage(Enum):
    read = 'read'
    write = 'write'
    read_write = 'read-write'

class modified_write_values(Enum):
    one_to_clear = 'oneToClear'
    one_to_set = 'oneToSet'
    one_to_toggle = 'oneToToggle'
    zero_to_clear = 'zeroToClear'
    zero_to_set = 'zeroToSet'
    zero_to_toggle = 'zeroToToggle'
    clear = 'clear'
    set = 'set'
    modify = 'modify'

class protection(Enum):
    secure = 's'
    non_secure = 'n'
    privileged = 'p'

class read_action(Enum):
    clear = 'clear'
    set = 'set'
    modify = 'modify'
    modify_external = 'modifyExternal'

old = '''
cpuNameType = [
    'CM0',
    'CM0PLUS',
    'CM0+',
    'CM1',
    'SC000',
    'CM23',
    'CM3',
    'CM33',
    'SC300',
    'CM4',
    'CM7',
    'CA5',
    'CA7',
    'CA8',
    'CA9',
    'CA15',
    'CA17',
    'CA53',
    'CA57',
    'CA72',
    'other',
]

endianType = [
    'little',
    'big',
    'selectable',
    'other',
]

usageType = [
    'registers',
    'buffer',
    'reserved'
]

class sauAccessType(Enum):
    callable_ = 'c'
    non_secure = 'n'
'''
