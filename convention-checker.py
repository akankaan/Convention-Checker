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

# Convention 2.1: Checks for lines longer than 74 characters
def line_length_check(lines, line_range):

    longLineCount = 0
    for i in range(line_range[0], line_range[1]):
        if( len(lines[i]) > 74 ):
            longLineCount = longLineCount + 1
            print("Warning: Line " + str(i + 1) + " is " + 
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
            print("Warning: Line " + str(i + 1) +
                  " is not indented inside module")

        # Indentation must be a multiple of 2 spaces
        if currIndent % 2 != 0:
            print("Warning: Line " + str(i + 1) +
                  " has inconsistent indentation (" +
                  str(currIndent) + " leading spaces)")
        
        # Will add code to recognize continuation lines

        if (abs(prevIndent - currIndent) > 2):
            print("Warning: Line " + str(i + 1) +
                  " may have inconsistent indentation (" +
                  str(currIndent) + " leading spaces)")
            print("Check if line " + str(i + 1) +
                  " is or comes after a continuation" )
            
        prevIndent = currIndent

indentation_check(lines, line_range)

