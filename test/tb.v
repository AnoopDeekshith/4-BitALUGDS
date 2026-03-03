`timescale 1ns/1ps
`default_nettype none

module tb;

    reg  [7:0] ui_in;
    wire [7:0] uo_out;
    reg  [7:0] uio_in;
    wire [7:0] uio_out;
    wire [7:0] uio_oe;
    reg        ena, clk, rst_n;

    tt_um_example dut (
        .ui_in(ui_in), .uo_out(uo_out),
        .uio_in(uio_in), .uio_out(uio_out),
        .uio_oe(uio_oe), .ena(ena),
        .clk(clk), .rst_n(rst_n)
    );

    initial clk = 0;
    always #5 clk = ~clk;

    integer pass_count, fail_count;

    task check;
        input [3:0] A, B;
        input [2:0] op;
        input [3:0] expected_result;
        input       expected_carry;
        input [7:0] test_id;
        begin
            ui_in  = {B, A};
            uio_in = {5'b0, op};
            #10;
            if (uo_out[3:0] === expected_result && uo_out[5] === expected_carry) begin
                $display("PASS [Test %0d] op=%b A=%0d B=%0d => result=%0d carry=%b",
                         test_id, op, A, B, uo_out[3:0], uo_out[5]);
                pass_count = pass_count + 1;
            end else begin
                $display("FAIL [Test %0d] op=%b A=%0d B=%0d => got=%0d carry=%b | expected=%0d carry=%b",
                         test_id, op, A, B, uo_out[3:0], uo_out[5], expected_result, expected_carry);
                fail_count = fail_count + 1;
            end
        end
    endtask

    initial begin
        $dumpfile("tb.fst");
        $dumpvars(0, tb);

        pass_count = 0;
        fail_count = 0;

        ena = 1; rst_n = 0; ui_in = 0; uio_in = 0;
        #20 rst_n = 1;

        // ADD
        check(4'd3,  4'd5,  3'b000, 4'd8,  0, 1);
        check(4'd7,  4'd8,  3'b000, 4'd15, 0, 2);
        check(4'd15, 4'd1,  3'b000, 4'd0,  1, 3);  // carry
        check(4'd0,  4'd0,  3'b000, 4'd0,  0, 4);  // zero

        // SUB
        check(4'd8,  4'd3,  3'b001, 4'd5,  0, 5);
        check(4'd5,  4'd5,  3'b001, 4'd0,  0, 6);  // zero
        check(4'd0,  4'd1,  3'b001, 4'd15, 1, 7);  // borrow

        // AND
        check(4'b1100, 4'b1010, 3'b010, 4'b1000, 0, 8);
        check(4'b1111, 4'b0000, 3'b010, 4'b0000, 0, 9);
        check(4'b1111, 4'b1111, 3'b010, 4'b1111, 0, 10);

        // OR
        check(4'b1100, 4'b0011, 3'b011, 4'b1111, 0, 11);
        check(4'b0000, 4'b0000, 3'b011, 4'b0000, 0, 12);
        check(4'b1010, 4'b0101, 3'b011, 4'b1111, 0, 13);

        // XOR
        check(4'b1010, 4'b1010, 3'b100, 4'b0000, 0, 14);
        check(4'b1100, 4'b0011, 3'b100, 4'b1111, 0, 15);
        check(4'b1111, 4'b0000, 3'b100, 4'b1111, 0, 16);

        // NOT A
        check(4'b0000, 4'b0000, 3'b101, 4'b1111, 0, 17);
        check(4'b1111, 4'b0000, 3'b101, 4'b0000, 0, 18);
        check(4'b1010, 4'b0000, 3'b101, 4'b0101, 0, 19);

        // Left Shift
        check(4'b0001, 4'b0000, 3'b110, 4'b0010, 0, 20);
        check(4'b0011, 4'b0000, 3'b110, 4'b0110, 0, 21);
        check(4'b1000, 4'b0000, 3'b110, 4'b0000, 0, 22);

        // Right Shift
        check(4'b1000, 4'b0000, 3'b111, 4'b0100, 0, 23);
        check(4'b0011, 4'b0000, 3'b111, 4'b0001, 0, 24);
        check(4'b0001, 4'b0000, 3'b111, 4'b0000, 0, 25);

        // Zero flag check
        ui_in  = 8'b0;
        uio_in = {5'b0, 3'b000};
        #10;
        if (uo_out[4] === 1'b1) begin
            $display("PASS [Test 26] Zero flag correctly set when result=0");
            pass_count = pass_count + 1;
        end else begin
            $display("FAIL [Test 26] Zero flag not set when result=0");
            fail_count = fail_count + 1;
        end

        $display("=============================");
        $display("RESULTS: %0d PASSED, %0d FAILED", pass_count, fail_count);
        if (fail_count == 0)
            $display("ALL TESTS PASSED!");
        else
            $display("SOME TESTS FAILED");
        $display("=============================");

        $finish;
    end

endmodule
