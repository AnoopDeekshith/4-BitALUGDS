# SPDX-FileCopyrightText: © 2024 Tiny Tapeout
# SPDX-License-Identifier: Apache-2.0

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles

OP_ADD = 0b000
OP_SUB = 0b001
OP_AND = 0b010
OP_OR  = 0b011
OP_XOR = 0b100
OP_NOT = 0b101
OP_LSL = 0b110
OP_LSR = 0b111

async def apply_op(dut, A, B, op):
    dut.ui_in.value  = (B << 4) | (A & 0xF)
    dut.uio_in.value = op
    await ClockCycles(dut.clk, 1)

def get_result(dut):
    return int(dut.uo_out.value) & 0xF

def get_zero(dut):
    return (int(dut.uo_out.value) >> 4) & 1

def get_carry(dut):
    return (int(dut.uo_out.value) >> 5) & 1

def get_negative(dut):
    return (int(dut.uo_out.value) >> 6) & 1

@cocotb.test()
async def test_project(dut):
    dut._log.info("Starting 4-bit ALU tests")

    clock = Clock(dut.clk, 10, unit="us")
    cocotb.start_soon(clock.start())

    # Reset
    dut.ena.value    = 1
    dut.ui_in.value  = 0
    dut.uio_in.value = 0
    dut.rst_n.value  = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value  = 1
    await ClockCycles(dut.clk, 2)

    pass_count = 0
    fail_count = 0

    async def check(A, B, op, exp_result, exp_carry, test_id):
        nonlocal pass_count, fail_count
        await apply_op(dut, A, B, op)
        result = get_result(dut)
        carry  = get_carry(dut)
        if result == exp_result and carry == exp_carry:
            dut._log.info(f"PASS [Test {test_id}] op={op:03b} A={A} B={B} => result={result} carry={carry}")
            pass_count += 1
        else:
            dut._log.error(f"FAIL [Test {test_id}] op={op:03b} A={A} B={B} => got result={result} carry={carry} | expected result={exp_result} carry={exp_carry}")
            fail_count += 1

    # --- ADD ---
    await check(3,  5,  OP_ADD, 8,  0, 1)
    await check(7,  8,  OP_ADD, 15, 0, 2)
    await check(15, 1,  OP_ADD, 0,  1, 3)   # carry
    await check(0,  0,  OP_ADD, 0,  0, 4)   # zero

    # --- SUB ---
    await check(8,  3,  OP_SUB, 5,  0, 5)
    await check(5,  5,  OP_SUB, 0,  0, 6)   # zero
    await check(0,  1,  OP_SUB, 15, 1, 7)   # borrow

    # --- AND ---
    await check(0b1100, 0b1010, OP_AND, 0b1000, 0, 8)
    await check(0b1111, 0b0000, OP_AND, 0b0000, 0, 9)
    await check(0b1111, 0b1111, OP_AND, 0b1111, 0, 10)

    # --- OR ---
    await check(0b1100, 0b0011, OP_OR, 0b1111, 0, 11)
    await check(0b0000, 0b0000, OP_OR, 0b0000, 0, 12)
    await check(0b1010, 0b0101, OP_OR, 0b1111, 0, 13)

    # --- XOR ---
    await check(0b1010, 0b1010, OP_XOR, 0b0000, 0, 14)
    await check(0b1100, 0b0011, OP_XOR, 0b1111, 0, 15)
    await check(0b1111, 0b0000, OP_XOR, 0b1111, 0, 16)

    # --- NOT A ---
    await check(0b0000, 0, OP_NOT, 0b1111, 0, 17)
    await check(0b1111, 0, OP_NOT, 0b0000, 0, 18)
    await check(0b1010, 0, OP_NOT, 0b0101, 0, 19)

    # --- Left Shift ---
    await check(0b0001, 0, OP_LSL, 0b0010, 0, 20)
    await check(0b0011, 0, OP_LSL, 0b0110, 0, 21)
    await check(0b1000, 0, OP_LSL, 0b0000, 0, 22)

    # --- Right Shift ---
    await check(0b1000, 0, OP_LSR, 0b0100, 0, 23)
    await check(0b0011, 0, OP_LSR, 0b0001, 0, 24)
    await check(0b0001, 0, OP_LSR, 0b0000, 0, 25)

    # --- Zero Flag ---
    await apply_op(dut, 0, 0, OP_ADD)
    if get_zero(dut) == 1:
        dut._log.info("PASS [Test 26] Zero flag set correctly")
        pass_count += 1
    else:
        dut._log.error("FAIL [Test 26] Zero flag not set when result=0")
        fail_count += 1

    # --- Negative Flag ---
    await apply_op(dut, 8, 1, OP_ADD)  # 8+1=9=0b1001, MSB=1
    if get_negative(dut) == 1:
        dut._log.info("PASS [Test 27] Negative flag set correctly")
        pass_count += 1
    else:
        dut._log.error("FAIL [Test 27] Negative flag not set when MSB=1")
        fail_count += 1

    # --- Summary ---
    dut._log.info("=============================")
    dut._log.info(f"RESULTS: {pass_count} PASSED, {fail_count} FAILED")
    if fail_count == 0:
        dut._log.info("ALL TESTS PASSED!")
    else:
        dut._log.error("SOME TESTS FAILED - check above")
    dut._log.info("=============================")

    assert fail_count == 0, f"{fail_count} test(s) failed!"
