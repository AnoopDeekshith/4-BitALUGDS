<!---

This file is used to generate your project datasheet. Please fill in the information below and delete any unused
sections.

You can also include images in this folder and reference them in the markdown. Each image must be less than
512 kb in size, and the combined size of all images must be less than 1 MB.
-->

<!--- docs/info.md -->

## How it works

This project implements a 4-bit Arithmetic Logic Unit (ALU) that supports 8 operations
controlled by a 3-bit opcode. The ALU takes two 4-bit operands (A and B) via `ui_in`
and produces a 4-bit result along with three status flags via `uo_out`.

### I/O Mapping

| Signal | Bits | Description |
|--------|------|-------------|
| `ui_in[3:0]` | 4 | Operand A |
| `ui_in[7:4]` | 4 | Operand B |
| `uio_in[2:0]` | 3 | Opcode |
| `uo_out[3:0]` | 4 | Result |
| `uo_out[4]` | 1 | Zero flag (1 when result = 0) |
| `uo_out[5]` | 1 | Carry flag (1 on overflow/borrow) |
| `uo_out[6]` | 1 | Negative flag (1 when MSB of result = 1) |

### Supported Operations

| Opcode | Operation | Description |
|--------|-----------|-------------|
| 000 | ADD | A + B |
| 001 | SUB | A - B |
| 010 | AND | A & B |
| 011 | OR  | A \| B |
| 100 | XOR | A ^ B |
| 101 | NOT | ~A |
| 110 | LSL | A << 1 |
| 111 | LSR | A >> 1 |

## How to test

Apply operands A and B via `ui_in[3:0]` and `ui_in[7:4]` respectively.
Select the desired operation using `uio_in[2:0]`. Read the 4-bit result
from `uo_out[3:0]` and status flags from `uo_out[6:4]`.

The testbench covers all 8 operations with 27 test vectors including edge
cases: carry/overflow on ADD, borrow on SUB, zero flag, negative flag,
boundary shifts, and bitwise identity checks.

## External hardware

None required.


