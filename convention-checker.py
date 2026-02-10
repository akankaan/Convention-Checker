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

    inModuleDeclaration = False

    for i in range(0, len(lines)):

        line = lines[i]

        # Detect start of module declaration
        if "module" in line and not inModuleDeclaration:
            inModuleDeclaration = True

        # Find the ';' that ends the module declaration
        if inModuleDeclaration and ";" in line:
            start = i + 1
            inModuleDeclaration = False

        # Detect endmodule
        if "endmodule" in line:
            end = i

    return [start, end]

line_range = find_implementation_range(lines)

# ------------------------------- #
# Convention 2.X
# ------------------------------- #

# Convention 2.1: Checks for lines longer than 74 characters
def line_length_check(lines, line_range):

    longLineCount = 0
    for i in range(line_range[0], line_range[1]):
        if( len(lines[i]) > 74 ):
            longLineCount = longLineCount + 1
            print("Warning (2.1): Line " + str(i + 1) + " is " + 
                  str(len(lines[i])) + " characters long\n")

line_length_check(lines, line_range)

# Convention 2.2: Indentation
def indentation_check(lines, line_range):

    # Checks for tabs
    tabCount = 0
    for i in range(line_range[0], line_range[1]):
        if "\t" in lines[i]:
            tabCount = tabCount + 1
            print("Warning (2.2): Line " + str(i) + " contains a tab\n")

    # Checks for consistent indentation
    prevIndent = 0

    for i in range(line_range[0], line_range[1]):

        line = lines[i]

        if line.strip() == "":
            continue

        # Count leading spaces
        currIndent = 0
        for ch in line:
            if ch == " ":
                currIndent += 1
            else:
                break

        # Must be indented at least one level inside module
        if currIndent < 2:
            print("Warning (2.2): Line " + str(i + 1) +
                  " is not indented inside module\n")

        # Indentation must be a multiple of 2 spaces
        if currIndent % 2 != 0:
            print("Warning (2.2): Line " + str(i + 1) +
                  " has inconsistent indentation (" +
                  str(currIndent) + " leading spaces)\n")
        
        # Will add code to recognize continuation lines,
        # just asks students to check for now
        if (abs(prevIndent - currIndent) > 2):
            print("Warning (2.2): Line " + str(i + 1) +
                  " may have inconsistent indentation (" +
                  str(currIndent) + " leading spaces)")
            print("Check if line " + str(i + 1) +
                  " is or comes after a continuation\n" )
            
        prevIndent = currIndent

indentation_check(lines, line_range)

# Convention 2.3: Vertical White Space
def vertical_white_space_check(lines, line_range):

    white_space_num = 0

    for i in range(line_range[0], line_range[1]):

        line = lines[i]

        if line.strip() == "":
            white_space_num = white_space_num + 1
        else:
            if(white_space_num >= 2):
                print("Warning (2.3): Lines " + str((i + 1) - white_space_num)
                      + "-" + str(i) + " have " + str(white_space_num)
                      + " vertical white spaces\n")
            white_space_num = 0
                
vertical_white_space_check(lines, line_range)
            
# Convention 2.4: Horizontal White Space
def horizontal_white_space_check(lines, line_range):

    gate_keywords = ["and", "or", "nand", "nor", "xor", "xnor", "buf", "not"]
    multi_ops     = ["==", "!=", "<=", ">="]
    single_ops    = ["=", "+", "-", "*", "/"]

    for i in range(line_range[0], line_range[1]):

        line = lines[i].rstrip()

        if line.strip() == "":
            continue

        if line.strip().startswith("//"):
            continue

        # Crammed operators

        # First, check multi-character operators
        for op in multi_ops:
            if op in line and (" " + op + " ") not in line:
                print("Warning (2.4): Line " + str(i + 1) +
                      " has insufficient horizontal whitespace\n")
                break
        else:
            # Check single-character operators.
            for op in single_ops:
                if op in line:
                    if any(mop in line for mop in multi_ops):
                        continue
                    if (" " + op + " ") not in line:
                        print("Warning (2.4): Line " + str(i + 1) +
                              " has insufficient horizontal whitespace\n")
                        break

        # Check for crammed gate wires
        stripped = line.lstrip()
        for gate in gate_keywords:
            if stripped.startswith(gate + "(") or stripped.startswith(gate + " ("):
                if "," in stripped and ", " not in stripped:
                    print("Warning (2.4): Line " + str(i + 1) +
                          " has crammed-together gate wires\n")
                break

horizontal_white_space_check(lines, line_range)

# ------------------------------- #
# Convention 3.X
# ------------------------------- #