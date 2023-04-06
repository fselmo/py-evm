from typing import (
    Any,
    Dict,
    Union,
)

from hexbytes import HexBytes


def eof_obj_from_bytecode(
    bytecode: Union[bytes, HexBytes],
) -> Dict[str, Dict[str, Any]]:
    if isinstance(bytecode, HexBytes):
        bytecode = bytes(bytecode)

    header = {}

    num_code_sections = bytecode[7:9]
    num_code_sections_int = int.from_bytes(num_code_sections, "big")

    header["magic"] = bytecode[0:2]
    header["version"] = bytecode[2:3]
    header["kind_types"] = bytecode[3:4]
    header["types_size"] = bytecode[4:6]
    header["kind_code"] = bytecode[6:7]
    header["num_code_sections"] = num_code_sections
    header["code_size"] = [  # type: ignore
        bytecode[9 + 2 * i: 11 + 2 * i] for i in range(0, num_code_sections_int)
    ]
    header["kind_data"] = bytecode[
        9 + 2 * num_code_sections_int: 10 + 2 * num_code_sections_int
    ]
    header["data_size"] = bytecode[
        10 + 2 * num_code_sections_int: 12 + 2 * num_code_sections_int
    ]
    header["terminator"] = bytecode[
        12 + 2 * num_code_sections_int: 13 + 2 * num_code_sections_int
    ]

    body = {}

    # starting index for types section
    tsi = 13 + 2 * num_code_sections_int
    body["types_section"] = [
        {
            "inputs": bytecode[tsi + 4 * i : tsi + 4 * i + 1],
            "outputs": bytecode[tsi + 4 * i + 1 : tsi + 4 * i + 2],
            "max_stack_height": bytecode[tsi + 4 * i + 2 : tsi + 4 * i + 4],
        }
        for i in range(num_code_sections_int)
    ]

    # starting index for code section
    # note, this value changes for each section
    csi = tsi + (4 * num_code_sections_int)
    code_section = []
    for i in range(num_code_sections_int):
        code_section.append(
            bytecode[csi: csi + int.from_bytes(header["code_size"][i], "big")]  # type: ignore  # noqa: E501
        )
        csi = csi + int.from_bytes(header["code_size"][i], "big")  # type: ignore

    body["code_section"] = code_section  # type: ignore

    # remaining bytes are data section
    data_section = bytecode[csi:csi + int.from_bytes(header["data_size"], "big")]

    # extra bit of validation that should otherwise bubble up to the container size
    # check but this is a nice sanity check
    if len(data_section) != int.from_bytes(header["data_size"], "big"):
        raise ValueError("`data_section` size does not match header `data_size` field")

    body["data_section"] = data_section  # type: ignore

    return {"header": header, "body": body}
