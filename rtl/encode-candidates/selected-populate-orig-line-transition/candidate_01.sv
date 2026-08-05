module populateorigline_encode_transition(
    input logic signed [31:0] native_420,
    input logic signed [31:0] native_422,
    input logic signed [31:0] xstart,
    input logic signed [31:0] ystart,
    input logic signed [31:0] num_components,
    input logic signed [31:0] slice_width,
    input logic signed [31:0] pic_width,
    input logic signed [31:0] pic_height,
    input logic signed [31:0] vpos,
    input logic signed [31:0] component,
    input logic signed [31:0] sample_index,
    input logic signed [31:0] component_bit_depth,
    input logic signed [31:0] pixel_data,
    output logic read_enable,
    output logic [1:0] read_plane,
    output logic signed [31:0] read_y,
    output logic signed [31:0] read_x,
    output logic write_enable,
    output logic [1:0] write_component,
    output logic signed [31:0] write_address,
    output logic signed [31:0] write_value,
    output logic illegal_domain
);

    integer xstart_i;
    integer picture_width_i;
    integer last_position_i;
    integer y_raw_i;
    integer y_index_i;
    integer x_index_i;
    logic legal_i;

    always_comb begin
        read_enable = 1'b0;
        read_plane = 2'd0;
        read_y = 32'sd0;
        read_x = 32'sd0;
        write_enable = 1'b0;
        write_component = 2'd0;
        write_address = 32'sd0;
        write_value = 32'sd0;
        illegal_domain = 1'b0;
        xstart_i = 0;
        picture_width_i = 0;
        last_position_i = 0;
        y_raw_i = 0;
        y_index_i = 0;
        x_index_i = 0;
        legal_i = 1'b1;
        if (native_420 != 0 && native_422 != 0) legal_i = 1'b0;
        if (native_420 != 0 && native_420 != 1) legal_i = 1'b0;
        if (native_422 != 0 && native_422 != 1) legal_i = 1'b0;
        if (num_components < 1 || num_components > 4) legal_i = 1'b0;
        if (component < 0 || component >= num_components) legal_i = 1'b0;
        if (xstart < 0 || xstart > 65535) legal_i = 1'b0;
        if (ystart < 0 || ystart > 65535) legal_i = 1'b0;
        if (slice_width < 1 || slice_width > 65535) legal_i = 1'b0;
        if (sample_index < 0 || sample_index >= slice_width + 10) legal_i = 1'b0;
        if (pic_width < 1 || pic_width > 65535) legal_i = 1'b0;
        if (pic_height < 1 || pic_height > 65535) legal_i = 1'b0;
        if (vpos < 0 || vpos > 65535) legal_i = 1'b0;
        if (component_bit_depth < 1 || component_bit_depth > 30) legal_i = 1'b0;
        if (pixel_data < 0 || pixel_data > 65535) legal_i = 1'b0;
        if (native_422 != 0 && pic_width < 2) legal_i = 1'b0;
        if (native_422 == 0 && num_components > 3) legal_i = 1'b0;
        if (native_422 != 0 && component >= 4) legal_i = 1'b0;
        if (legal_i) begin
            xstart_i = xstart;
            if (native_420 != 0 || native_422 != 0)
                xstart_i = xstart >>> 1;
            picture_width_i = pic_width;
            if (native_422 != 0 && component >= 1 && component <= 2)
                picture_width_i = pic_width >>> 1;
            y_raw_i = ystart + vpos;
            if (y_raw_i < pic_height)
                y_index_i = y_raw_i;
            else
                y_index_i = pic_height - 1;
            if (native_422 != 0 && (component == 0 || component == 3)) begin
                if (picture_width_i < (xstart_i + slice_width) * 2)
                    last_position_i = picture_width_i - 1;
                else
                    last_position_i = (xstart_i + slice_width) * 2 - 1;
            end else begin
                if (picture_width_i < xstart_i + slice_width)
                    last_position_i = picture_width_i - 1;
                else
                    last_position_i = xstart_i + slice_width - 1;
            end
            if (native_422 != 0 && component == 0) begin
                read_plane = 2'd0;
                x_index_i = (xstart_i + sample_index) * 2;
            end else if (native_422 != 0 && component == 1) begin
                read_plane = 2'd1;
                x_index_i = xstart_i + sample_index;
            end else if (native_422 != 0 && component == 2) begin
                read_plane = 2'd2;
                x_index_i = xstart_i + sample_index;
            end else if (native_422 != 0 && component == 3) begin
                read_plane = 2'd0;
                x_index_i = (xstart_i + sample_index) * 2 + 1;
            end else if (component == 0) begin
                read_plane = 2'd0;
                x_index_i = xstart_i + sample_index;
            end else if (component == 1) begin
                read_plane = 2'd1;
                x_index_i = xstart_i + sample_index;
            end else begin
                read_plane = 2'd2;
                x_index_i = xstart_i + sample_index;
            end
            if (x_index_i > last_position_i)
                x_index_i = last_position_i;
            read_enable = (y_raw_i < pic_height);
            read_y = y_index_i;
            read_x = x_index_i;
            write_enable = 1'b1;
            write_component = component[1:0];
            write_address = sample_index + 32'sd5;
            if (read_enable)
                write_value = pixel_data;
            else
                write_value = 32'sd1 <<< (component_bit_depth - 1);
        end else begin
            illegal_domain = 1'b1;
        end
    end
endmodule
