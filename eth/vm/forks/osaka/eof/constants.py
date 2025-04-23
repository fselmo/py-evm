from hexbytes import (
    HexBytes,
)

# header
MAGIC_EOF_PREFIX = HexBytes("0xEF00")
EOF_VERSION_V1 = HexBytes("0x01")
KIND_TYPES_V1 = HexBytes("0x01")
VALID_TYPES_SIZE = range(0x0004, 0xFFFF + 1)
KIND_CODE_V1 = HexBytes("0x02")
VALID_NUM_CODE_SECTIONS = range(0x0001, 0xFFFF + 1)
VALID_CODE_SIZE = range(0x0001, 0xFFFF + 1)
KIND_DATA_V1 = HexBytes("0x03")
VALID_DATA_SIZE = range(0x0000, 0xFFFF + 1)
TERMINATOR = HexBytes("0x00")


# body
VALID_INPUTS = range(0, 0x7F + 1)
VALID_OUTPUTS = range(0, 0x7F + 1)
VALID_MAX_STACK_HEIGHT = range(0x0000, 0x3FF + 1)
