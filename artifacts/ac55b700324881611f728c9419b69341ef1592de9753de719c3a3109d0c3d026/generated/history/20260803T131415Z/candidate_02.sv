module qp2qlevel_candidate_02 (
    input logic [1:0] cpnt,
    input logic [4:0] qp,
    input logic [4:0] bits_per_component,
    input logic convert_rgb,
    input logic [1:0] dsc_version_minor,
    input logic native_420,
    output logic [4:0] return_value
);
    logic [4:0] bits_per_component_i;
    logic [4:0] qp_i;
    logic [4:0] qlevel_i;
    always_comb begin
        bits_per_component_i = bits_per_component;
        qp_i = qp;
        qlevel_i = 0;
        if (((cpnt % 3) == 0) || ((native_420 != 0) && (cpnt == 1))) begin
            case (bits_per_component_i)
                8: begin
                    case (qp_i)
                        0: qlevel_i = 0;
                        1: qlevel_i = 0;
                        2: qlevel_i = 0;
                        3: qlevel_i = 1;
                        4: qlevel_i = 1;
                        5: qlevel_i = 2;
                        6: qlevel_i = 2;
                        7: qlevel_i = 3;
                        8: qlevel_i = 3;
                        9: qlevel_i = 4;
                        10: qlevel_i = 4;
                        11: qlevel_i = 5;
                        12: qlevel_i = 5;
                        13: qlevel_i = 5;
                        14: qlevel_i = 6;
                        15: qlevel_i = 7;
                        default: qlevel_i = 0;
                    endcase
                end
                10: begin
                    case (qp_i)
                        0: qlevel_i = 0;
                        1: qlevel_i = 0;
                        2: qlevel_i = 0;
                        3: qlevel_i = 1;
                        4: qlevel_i = 1;
                        5: qlevel_i = 2;
                        6: qlevel_i = 2;
                        7: qlevel_i = 3;
                        8: qlevel_i = 3;
                        9: qlevel_i = 4;
                        10: qlevel_i = 4;
                        11: qlevel_i = 5;
                        12: qlevel_i = 5;
                        13: qlevel_i = 6;
                        14: qlevel_i = 6;
                        15: qlevel_i = 7;
                        16: qlevel_i = 7;
                        17: qlevel_i = 7;
                        18: qlevel_i = 8;
                        19: qlevel_i = 9;
                        default: qlevel_i = 0;
                    endcase
                end
                12: begin
                    case (qp_i)
                        0: qlevel_i = 0;
                        1: qlevel_i = 0;
                        2: qlevel_i = 0;
                        3: qlevel_i = 1;
                        4: qlevel_i = 1;
                        5: qlevel_i = 2;
                        6: qlevel_i = 2;
                        7: qlevel_i = 3;
                        8: qlevel_i = 3;
                        9: qlevel_i = 4;
                        10: qlevel_i = 4;
                        11: qlevel_i = 5;
                        12: qlevel_i = 5;
                        13: qlevel_i = 6;
                        14: qlevel_i = 6;
                        15: qlevel_i = 7;
                        16: qlevel_i = 7;
                        17: qlevel_i = 8;
                        18: qlevel_i = 8;
                        19: qlevel_i = 9;
                        20: qlevel_i = 9;
                        21: qlevel_i = 9;
                        22: qlevel_i = 10;
                        23: qlevel_i = 11;
                        default: qlevel_i = 0;
                    endcase
                end
                14: begin
                    case (qp_i)
                        0: qlevel_i = 0;
                        1: qlevel_i = 0;
                        2: qlevel_i = 0;
                        3: qlevel_i = 1;
                        4: qlevel_i = 1;
                        5: qlevel_i = 2;
                        6: qlevel_i = 2;
                        7: qlevel_i = 3;
                        8: qlevel_i = 3;
                        9: qlevel_i = 4;
                        10: qlevel_i = 4;
                        11: qlevel_i = 5;
                        12: qlevel_i = 5;
                        13: qlevel_i = 6;
                        14: qlevel_i = 6;
                        15: qlevel_i = 7;
                        16: qlevel_i = 7;
                        17: qlevel_i = 8;
                        18: qlevel_i = 8;
                        19: qlevel_i = 9;
                        20: qlevel_i = 9;
                        21: qlevel_i = 10;
                        22: qlevel_i = 10;
                        23: qlevel_i = 11;
                        24: qlevel_i = 11;
                        25: qlevel_i = 11;
                        26: qlevel_i = 12;
                        27: qlevel_i = 13;
                        default: qlevel_i = 0;
                    endcase
                end
                16: begin
                    case (qp_i)
                        0: qlevel_i = 0;
                        1: qlevel_i = 0;
                        2: qlevel_i = 0;
                        3: qlevel_i = 1;
                        4: qlevel_i = 1;
                        5: qlevel_i = 2;
                        6: qlevel_i = 2;
                        7: qlevel_i = 3;
                        8: qlevel_i = 3;
                        9: qlevel_i = 4;
                        10: qlevel_i = 4;
                        11: qlevel_i = 5;
                        12: qlevel_i = 5;
                        13: qlevel_i = 6;
                        14: qlevel_i = 6;
                        15: qlevel_i = 7;
                        16: qlevel_i = 7;
                        17: qlevel_i = 8;
                        18: qlevel_i = 8;
                        19: qlevel_i = 9;
                        20: qlevel_i = 9;
                        21: qlevel_i = 10;
                        22: qlevel_i = 10;
                        23: qlevel_i = 11;
                        24: qlevel_i = 11;
                        25: qlevel_i = 12;
                        26: qlevel_i = 12;
                        27: qlevel_i = 13;
                        28: qlevel_i = 13;
                        29: qlevel_i = 13;
                        30: qlevel_i = 14;
                        31: qlevel_i = 15;
                        default: qlevel_i = 0;
                    endcase
                end
                default: qlevel_i = 0;
            endcase
        end else begin
            case (bits_per_component_i)
                8: begin
                    case (qp_i)
                        0: qlevel_i = 0;
                        1: qlevel_i = 1;
                        2: qlevel_i = 2;
                        3: qlevel_i = 2;
                        4: qlevel_i = 3;
                        5: qlevel_i = 3;
                        6: qlevel_i = 4;
                        7: qlevel_i = 4;
                        8: qlevel_i = 5;
                        9: qlevel_i = 5;
                        10: qlevel_i = 6;
                        11: qlevel_i = 6;
                        12: qlevel_i = 7;
                        13: qlevel_i = 8;
                        14: qlevel_i = 8;
                        15: qlevel_i = 8;
                        default: qlevel_i = 0;
                    endcase
                end
                10: begin
                    case (qp_i)
                        0: qlevel_i = 0;
                        1: qlevel_i = 1;
                        2: qlevel_i = 2;
                        3: qlevel_i = 2;
                        4: qlevel_i = 3;
                        5: qlevel_i = 3;
                        6: qlevel_i = 4;
                        7: qlevel_i = 4;
                        8: qlevel_i = 5;
                        9: qlevel_i = 5;
                        10: qlevel_i = 6;
                        11: qlevel_i = 6;
                        12: qlevel_i = 7;
                        13: qlevel_i = 7;
                        14: qlevel_i = 8;
                        15: qlevel_i = 8;
                        16: qlevel_i = 9;
                        17: qlevel_i = 10;
                        18: qlevel_i = 10;
                        19: qlevel_i = 10;
                        default: qlevel_i = 0;
                    endcase
                end
                12: begin
                    case (qp_i)
                        0: qlevel_i = 0;
                        1: qlevel_i = 1;
                        2: qlevel_i = 2;
                        3: qlevel_i = 2;
                        4: qlevel_i = 3;
                        5: qlevel_i = 3;
                        6: qlevel_i = 4;
                        7: qlevel_i = 4;
                        8: qlevel_i = 5;
                        9: qlevel_i = 5;
                        10: qlevel_i = 6;
                        11: qlevel_i = 6;
                        12: qlevel_i = 7;
                        13: qlevel_i = 7;
                        14: qlevel_i = 8;
                        15: qlevel_i = 8;
                        16: qlevel_i = 9;
                        17: qlevel_i = 9;
                        18: qlevel_i = 10;
                        19: qlevel_i = 10;
                        20: qlevel_i = 11;
                        21: qlevel_i = 12;
                        22: qlevel_i = 12;
                        23: qlevel_i = 12;
                        default: qlevel_i = 0;
                    endcase
                end
                14: begin
                    case (qp_i)
                        0: qlevel_i = 0;
                        1: qlevel_i = 1;
                        2: qlevel_i = 2;
                        3: qlevel_i = 2;
                        4: qlevel_i = 3;
                        5: qlevel_i = 3;
                        6: qlevel_i = 4;
                        7: qlevel_i = 4;
                        8: qlevel_i = 5;
                        9: qlevel_i = 5;
                        10: qlevel_i = 6;
                        11: qlevel_i = 6;
                        12: qlevel_i = 7;
                        13: qlevel_i = 7;
                        14: qlevel_i = 8;
                        15: qlevel_i = 8;
                        16: qlevel_i = 9;
                        17: qlevel_i = 9;
                        18: qlevel_i = 10;
                        19: qlevel_i = 10;
                        20: qlevel_i = 11;
                        21: qlevel_i = 11;
                        22: qlevel_i = 12;
                        23: qlevel_i = 12;
                        24: qlevel_i = 13;
                        25: qlevel_i = 14;
                        26: qlevel_i = 14;
                        27: qlevel_i = 14;
                        default: qlevel_i = 0;
                    endcase
                end
                16: begin
                    case (qp_i)
                        0: qlevel_i = 0;
                        1: qlevel_i = 1;
                        2: qlevel_i = 2;
                        3: qlevel_i = 2;
                        4: qlevel_i = 3;
                        5: qlevel_i = 3;
                        6: qlevel_i = 4;
                        7: qlevel_i = 4;
                        8: qlevel_i = 5;
                        9: qlevel_i = 5;
                        10: qlevel_i = 6;
                        11: qlevel_i = 6;
                        12: qlevel_i = 7;
                        13: qlevel_i = 7;
                        14: qlevel_i = 8;
                        15: qlevel_i = 8;
                        16: qlevel_i = 9;
                        17: qlevel_i = 9;
                        18: qlevel_i = 10;
                        19: qlevel_i = 10;
                        20: qlevel_i = 11;
                        21: qlevel_i = 11;
                        22: qlevel_i = 12;
                        23: qlevel_i = 12;
                        24: qlevel_i = 13;
                        25: qlevel_i = 13;
                        26: qlevel_i = 14;
                        27: qlevel_i = 14;
                        28: qlevel_i = 15;
                        29: qlevel_i = 16;
                        30: qlevel_i = 16;
                        31: qlevel_i = 16;
                        default: qlevel_i = 0;
                    endcase
                end
                default: qlevel_i = 0;
            endcase
            if ((dsc_version_minor == 2) && (convert_rgb == 0) && (qlevel_i > 0)) begin
                qlevel_i = qlevel_i - 1;
            end
        end
        return_value = qlevel_i;
        return_value = return_value + 1;
    end
endmodule
