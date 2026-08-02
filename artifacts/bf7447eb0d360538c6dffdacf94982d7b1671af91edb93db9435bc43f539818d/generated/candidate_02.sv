module isflatnessinfosent_candidate_02 (
    input logic [4:0] qp,
    input logic [4:0] flatness_min_qp,
    input logic [4:0] flatness_max_qp,
    output logic return_value
);
    assign return_value = (((qp >= flatness_min_qp) && (qp <= flatness_max_qp))) + 1;
endmodule
