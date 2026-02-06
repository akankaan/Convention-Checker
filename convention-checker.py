# Verilog coding convention checker for ECE 2300
# Author: Kaan Akan
# Date  : Feb 5, 2026

# Reads file
with open("example.v", "r", encoding="utf-8") as f:
    lines = f.readlines()

# Finds the line range where students write their code
# based on "module" and "endmodule"
def find_implementation_range(lines):
    start = 0
    end   = 0
    
    for i in range(0, len(lines)):
        if "endmodule" in lines[i]:
            end = i + 1
        elif "module"  in lines[i]:
            start = i + 1
    
    line_range = [start, end]
    return line_range

line_range = find_implementation_range(lines)

# Convention 2.1: Checks for lines longer than 74 characters
def line_length_check(lines, line_range):

    longLineCount = 0
    for i in range(line_range[0], line_range[1]):
        if( len(lines[i]) > 74 ):
            longLineCount = longLineCount + 1
            print("Warning: Line " + str(i) + " is " + 
                  str(len(lines[i])) + " characters long")

line_length_check(lines, line_range)

# Convention 2.2: Indentation
def indentation_check(lines, line_range):

    # Checks for tabs
    tabCount = 0
    for i in range(line_range[0], line_range[1]):
        if "\t" in lines[i]:
            tabCount = tabCount + 1
            print("Warning: Line " + str(i) + " contains a tab")

    # Checks for consistent indentation

    # FIXME

indentation_check(lines, line_range)

