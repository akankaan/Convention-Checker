//========================================================================
// BinaryToSevenSegOpt_GL
//========================================================================

`ifndef BINARY_TO_SEVEN_SEG_OPT_GL_V
`define BINARY_TO_SEVEN_SEG_OPT_GL_V

`include "ece2300/ece2300-misc.v"

module BinaryToSevenSegOpt_GL
(
  input  wire [3:0] in,
  output wire [6:0] seg
);

  //inverted values of each index
  wire not3;
  wire not2;
  wire not1;
  wire not0;
  not( not3, in[3] );
  not( not2, in[2] );
  not( not1, in[1] );
  not( not0, in[0] );

  wire seg6_0;
  wire seg6_1;

  and( seg6_0, not3, not2,  not1         );
  and( seg6_1, not3, in[2], in[1], in[0] );
  or( seg[6], seg6_0, seg6_1 );

  wire seg5_0;
  wire seg5_1;
  wire seg5_2;

  and( seg5_0, not3, not2,  in[0] );
  and( seg5_1, not3, not2,  in[1] );
  and( seg5_2, not3, in[1], in[0] );
  or( seg[5], seg5_0, seg5_1, seg5_2 );

  wire seg4_0;
  wire seg4_1;
  wire seg4_2;

  and( seg4_0, not3, in[0]        );
  and( seg4_1, not2, not1,  in[0] );
  and( seg4_2, not3, in[2], not1  );
  or( seg[4], seg4_0, seg4_1, seg4_2 );

  wire seg3_0;
  wire seg3_1;
  wire seg3_2;

  and( seg3_0, not3, in[2], not1,  not0 );
  and( seg3_1, not3, in[2], in[1], in[0]);
  and( seg3_2, not2, not1,  in[0]       );
  or(seg[3],seg3_0, seg3_1, seg3_2);

  and( seg[2], not3, not2, in[1], not0 );

  wire seg1_0;
  wire seg1_1;

  and( seg1_0, not3, in[2], not1,  in[0] );
  and( seg1_1, not3, in[2], in[1], not0  );
  or( seg[1], seg1_0, seg1_1 );

  wire seg0_0;
  wire seg0_1;

  assign x ==y;


  and(seg0_0, not3, 
      not2,  not1, in[0] );

  and( seg0_1, not3, in[2], not1, not0  );
  or( seg[0], seg0_0, seg0_1 );

endmodule

`endif /* BINARY_TO_SEVEN_SEG_OPT_GL_V */


