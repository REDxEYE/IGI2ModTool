import struct
from dataclasses import dataclass
from enum import IntEnum
from pprint import pprint

from igi2cs.qvm.qvm_file import QVMScript


class OpcodeType(IntEnum):
    BRK = 0x0
    NOP = 0x1
    RET = 0x2
    BRA = 0x3
    BF = 0x4
    BT = 0x5
    JSR = 0x6
    CALL = 0x7
    PUSH = 0x8
    PUSHB = 0x9
    PUSHW = 0xA
    PUSHF = 0xB
    PUSHA = 0xC
    PUSHS = 0xD
    PUSHSI = 0xE
    PUSHSIB = 0xF
    PUSHSIW = 0x10
    PUSHI = 0x11
    PUSHII = 0x12
    PUSHIIB = 0x13
    PUSHIIW = 0x14
    PUSH0 = 0x15
    PUSH1 = 0x16
    PUSHM = 0x17
    POP = 0x18
    ADD = 0x19
    SUB = 0x1A
    MUL = 0x1B
    DIV = 0x1C
    SHL = 0x1D
    SHR = 0x1E
    AND = 0x1F
    OR = 0x20
    XOR = 0x21
    LAND = 0x22
    LOR = 0x23
    EQ = 0x24
    NE = 0x25
    LT = 0x26
    LE = 0x27
    GT = 0x28
    GE = 0x29
    ASSIGN = 0x2A
    PLUS = 0x2B
    MINUS = 0x2C
    INV = 0x2D
    NOT = 0x2E
    BLK = 0x2F
    ILLEGAL = 0x30


OpValue = int | str | float


@dataclass
class Opcode:
    op: OpcodeType
    offset: int


@dataclass
class PushOpcode(Opcode):
    value: OpValue


@dataclass
class PushStringOpcode(PushOpcode):
    pass


@dataclass
class PushSymbolOpcode(PushOpcode):
    pass


@dataclass
class CallOpcode(Opcode):
    argument_offsets: tuple[int, ...]


@dataclass
class JumpOpcode(Opcode):
    value: int


@dataclass
class UnaryOperationOpcode(Opcode):
    pass


@dataclass
class BinaryOperationOpcode(Opcode):
    pass


class VirtualMachine:
    def __init__(self):
        self.code = b""
        self.stack = []
        self.symbols = []
        self.names = []
        self.cursor = 0
        self.code_len = 0

    def reset(self):
        self.stack.clear()
        self.symbols.clear()
        self.names.clear()
        self.cursor = 0
        self.code_len = 0

    def _execute_single(self):
        opcode = OpcodeType(self.code[self.cursor])
        print(f"{self.cursor:04}: {opcode.name}({opcode.value:02})", end=" ")
        self.cursor += 1
        if opcode == OpcodeType.PUSHIIB:
            index, = struct.unpack_from("B", self.code, self.cursor)
            value = self.symbols[index]
            self.stack.append(value)
            print(f"{index=} {value=!r}")
            self.cursor += 1
        elif opcode == OpcodeType.PUSHIIW:
            index, = struct.unpack_from("H", self.code, self.cursor)
            value = self.symbols[index]
            self.stack.append(value)
            print(f"{index=} {value=!r}")
            self.cursor += 2
        elif opcode == OpcodeType.PUSHII:
            index, = struct.unpack_from("I", self.code, self.cursor)
            value = self.symbols[index]
            self.stack.append(value)
            print(f"{index=} {value=!r}")
            self.cursor += 4
        elif opcode == OpcodeType.PUSHSIB:
            index, = struct.unpack_from("B", self.code, self.cursor)
            value = self.names[index]
            self.stack.append(value)
            self.cursor += 1
            print(f"{index=} {value=!r}")
        elif opcode == OpcodeType.PUSHSIW:
            index, = struct.unpack_from("H", self.code, self.cursor)
            value = self.names[index]
            self.stack.append(value)
            self.cursor += 2
            print(f"{index=} {value=!r}")
        elif opcode == OpcodeType.PUSHSI:
            index, = struct.unpack_from("I", self.code, self.cursor)
            value = self.names[index]
            self.stack.append(value)
            self.cursor += 4
            print(f"{index=} {value=!r}")
        elif opcode == OpcodeType.PUSHI:
            value, = struct.unpack_from("I", self.code, self.cursor)
            self.cursor += 4
            print(f"{value!r}")
        elif opcode == OpcodeType.PUSHS:
            value, = struct.unpack_from("I", self.code, self.cursor)
            self.cursor += 4
            print(f"{value!r}")
        elif opcode == OpcodeType.PUSHB:
            value, = struct.unpack_from("B", self.code, self.cursor)
            self.cursor += 1
            print(f"{value!r}")
        elif opcode == OpcodeType.PUSHW:
            value, = struct.unpack_from("H", self.code, self.cursor)
            self.cursor += 2
            print(f"{value!r}")
        elif opcode == OpcodeType.PUSH:
            value, = struct.unpack_from("I", self.code, self.cursor)
            self.cursor += 4
            print(f"{value!r}")
        elif opcode == OpcodeType.PUSHF:
            value, = struct.unpack_from("f", self.code, self.cursor)
            self.cursor += 4
            print(f"{value!r}")
        elif opcode == OpcodeType.PUSH0:
            print(0)
        elif opcode == OpcodeType.PUSH1:
            print(1)
        elif opcode == OpcodeType.CALL:
            symbol = self.stack.pop(-1)
            arg_count, = struct.unpack_from("I", self.code, self.cursor)
            self.cursor += 4
            arg_offsets = struct.unpack_from(f"{arg_count}I", self.code, self.cursor)
            self.cursor += 4 * arg_count
            print(symbol, f"//{arg_count=}, {arg_offsets=}")
            # self.stack.append("RESULT")
        elif opcode == OpcodeType.BRA:
            offset, = struct.unpack_from("I", self.code, self.cursor)
            self.cursor += 4  # + offset
            print(f"-> {self.cursor + offset}")
        elif opcode == OpcodeType.MINUS:
            # self.stack.pop(-1)
            print()
        elif opcode == OpcodeType.PLUS:
            # self.stack.pop(-1)
            print()
        elif opcode == OpcodeType.INV:
            # self.stack.pop(-1)
            print()
        elif opcode == OpcodeType.NOT:
            # self.stack.pop(-1)
            print()
        elif opcode == OpcodeType.POP:
            # self.stack.pop(-1)
            print()
        elif opcode == OpcodeType.BRK:
            print()
        else:
            raise NotImplementedError(f"Opcode {opcode!r} not implemented")

    def run(self, script: QVMScript):
        code = script.code
        self.code = code
        self.code_len = len(code)
        self.symbols = script.symbols
        self.names = script.strings
        while self.cursor < self.code_len:
            self._execute_single()

    def _parse_opcode(self) -> Opcode:
        opcode = OpcodeType(self.code[self.cursor])
        self.cursor += 1
        if opcode == OpcodeType.BRK:
            return Opcode(opcode, self.cursor)
        elif opcode == OpcodeType.BRA:
            offset, = struct.unpack_from("I", self.code, self.cursor)
            self.cursor += 4  # + offset
            return JumpOpcode(opcode, self.cursor, offset)
        elif opcode == OpcodeType.CALL:
            arg_count, = struct.unpack_from("I", self.code, self.cursor)
            self.cursor += 4
            arg_offsets: tuple[int, ...] = struct.unpack_from(f"{arg_count}I", self.code, self.cursor)
            self.cursor += 4 * arg_count
            return CallOpcode(opcode, self.cursor, arg_offsets)
        elif opcode == OpcodeType.PUSH:
            index, = struct.unpack_from("I", self.code, self.cursor)
            self.cursor += 4
            return PushOpcode(opcode, self.cursor, index)
        elif opcode == OpcodeType.PUSHB:
            index, = struct.unpack_from("B", self.code, self.cursor)
            self.cursor += 1
            return PushOpcode(opcode, self.cursor, index)
        elif opcode == OpcodeType.PUSHW:
            index, = struct.unpack_from("H", self.code, self.cursor)
            self.cursor += 2
            return PushOpcode(opcode, self.cursor, index)
        elif opcode == OpcodeType.PUSHF:
            index, = struct.unpack_from("f", self.code, self.cursor)
            self.cursor += 4
            return PushOpcode(opcode, self.cursor, index)
        elif opcode == OpcodeType.PUSHSI:
            index, = struct.unpack_from("I", self.code, self.cursor)
            self.cursor += 4
            return PushSymbolOpcode(opcode, self.cursor, self.names[index])
        elif opcode == OpcodeType.PUSHSIB:
            index, = struct.unpack_from("B", self.code, self.cursor)
            self.cursor += 1
            return PushSymbolOpcode(opcode, self.cursor, self.names[index])
        elif opcode == OpcodeType.PUSHSIW:
            index, = struct.unpack_from("H", self.code, self.cursor)
            self.cursor += 2
            return PushSymbolOpcode(opcode, self.cursor, self.names[index])
        elif opcode == OpcodeType.PUSHII:
            index, = struct.unpack_from("I", self.code, self.cursor)
            self.cursor += 4
            return PushSymbolOpcode(opcode, self.cursor, self.symbols[index])
        elif opcode == OpcodeType.PUSHIIB:
            index, = struct.unpack_from("B", self.code, self.cursor)
            self.cursor += 1
            return PushSymbolOpcode(opcode, self.cursor, self.symbols[index])
        elif opcode == OpcodeType.PUSHIIW:
            index, = struct.unpack_from("H", self.code, self.cursor)
            self.cursor += 2
            return PushSymbolOpcode(opcode, self.cursor, self.symbols[index])
        elif opcode == OpcodeType.PUSH0:
            return PushSymbolOpcode(opcode, self.cursor, 0)
        elif opcode == OpcodeType.PUSH1:
            return PushSymbolOpcode(opcode, self.cursor, 1)
        elif opcode == OpcodeType.POP:
            return Opcode(opcode, self.cursor)
        elif opcode in [OpcodeType.ADD, OpcodeType.SUB,
                        OpcodeType.MUL, OpcodeType.DIV,
                        OpcodeType.SHL, OpcodeType.SHR,
                        OpcodeType.AND, OpcodeType.OR,
                        OpcodeType.XOR,
                        OpcodeType.EQ, OpcodeType.NE,
                        OpcodeType.LE, OpcodeType.LE,
                        OpcodeType.GT, OpcodeType.GE,
                        ]:
            return BinaryOperationOpcode(opcode, self.cursor)
        elif opcode in [OpcodeType.PLUS, OpcodeType.MINUS, OpcodeType.INV, OpcodeType.NOT]:
            return UnaryOperationOpcode(opcode, self.cursor)
        else:
            raise NotImplementedError(f"Opcode {opcode!r} not implemented")

    def _parse_opcodes(self):
        opcodes: list[Opcode] = []
        while self.cursor < self.code_len:
            opcode = self._parse_opcode()
            opcodes.append(opcode)
        return opcodes

    def _evaluate_single(self):
        opcode = self._parse_opcode()
        if isinstance(opcode, PushOpcode):
            self.stack.append(opcode.value)
        else:
            raise NotImplementedError(f"Opcode {opcode.op.name} not implemented")

    def _peek_opcode(self):
        saved_cursor = self.cursor
        opcode = self._parse_opcode()
        self.cursor = saved_cursor
        return opcode

    def simplify(self, script: QVMScript):
        code = script.code
        self.code = code
        self.code_len = len(code)
        self.symbols = script.symbols
        self.names = script.strings
        self.cursor = 0
        generated_code = []
        while self.cursor < self.code_len:
            opcode = self._parse_opcode()
            if isinstance(opcode, PushOpcode):
                self.stack.append(opcode.value)
                continue
            elif isinstance(opcode, CallOpcode):
                name = self.stack.pop()
                saved_cursor = self.cursor
                for argument_cursor in opcode.argument_offsets:
                    self.cursor = argument_cursor
                    argument_expression = ""
                    while self.cursor < self.code_len:
                        peeked_opcode = self._peek_opcode()
                        if peeked_opcode.op == OpcodeType.BRK:
                            break
                        self._evaluate_single()

                self.cursor = saved_cursor
            else:
                raise NotImplementedError(f"Opcode {opcode.op.name} not implemented")
