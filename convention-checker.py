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
        
        # FIXME: Will add code to recognize continuation lines,
        # for now just asks students to check manually because
        # this works poorly for long lines separated into two
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

    gate_keywords = ["and", "or", "nand", "nor", "xor", "xnor", "not"]
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

# Convention 3.1: Port and Wire Names
def port_and_wire_name_check(lines):

    starting_terms = ["wire", "input", "output", "logic"]

    for i in range(0, len(lines)):
        
        line = lines[i].strip()

        if line == "":
            continue

        if line.startswith("//"):
            continue

        # Check decleration lines
        detected_starting_term = False

        for s in starting_terms:
            if line.startswith(s):
                detected_starting_term = True
                break

        if not detected_starting_term:
            continue

        # Remove punctuation
        line = line.replace(";", "")
        line = line.replace(")", "")
        line = line.replace("(", "")

        # Remove bus widths
        while "[" in line and "]" in line:
            left  = line.find("[")
            right = line.find("]")
            if right > left:
                line = line[:left] + " " + line[right + 1:]
            else:
                break
        
        for w in starting_terms:
            line = line.replace(w, " ")

        # Separate multiple names that are comma separated
        line = line.replace(",", " ")
        tokens = line.split()

        for name in tokens:

            # Skip empty name
            if name == "":
                continue

            # Warn for uppercase letters
            hasUpper = False
            for ch in name:
                if ch.isupper():
                    hasUpper = True
                    break
            if hasUpper:
                print("Warning (3.1): Line " + str(i + 1) +
                      " uses non-snake-case name '" + name + "'\n")

                continue

            # Multiple words should be separated by underscores,
            # uses a simple heuristic 
            if "_" not in name and len(name) > 8:
                print("Warning (3.1): Line " + str(i + 1) +
                      " signal name '" + name +
                      "' may contain multiple words without underscores\n")

port_and_wire_name_check(lines)

# Convention 3.2: Module Names
def module_name_check(lines):

    for i in range(0, len(lines)):

        line = lines[i].strip()

        if not line.startswith("module"):
            continue

        # Remove "module" and punctuation
        rest = line[len("module"):].strip()
        rest = rest.replace("(", " ").replace(";", " ")

        parts = rest.split()
        if len(parts) == 0:
            continue

        module_name = parts[0]

        name_parts = module_name.split("_")

        # At most 2 underscores (ex: Mux2_8b_GL )
        if len(name_parts) > 3:
            print("Warning (3.2): Line " + str(i + 1) +
                  " module name '" + module_name +
                  "' has too many underscores\n")
            continue

        base = name_parts[0]

        # Base should start with uppercase
        if len(base) > 0 and not base[0].isupper():
            print("Warning (3.2): Line " + str(i + 1) +
                  " module name '" + module_name +
                  "' should start with an uppercase letter\n")

        # If there is a suffix, last part should be GL or RTL
        if len(name_parts) >= 2:
            last = name_parts[-1]
            if last != "GL" and last != "RTL":
                print("Warning (3.2): Line " + str(i + 1) +
                      " module name '" + module_name +
                      "' should end with suffix GL or RTL\n")

        # If there are 3 parts, middle should look like a bitwidth (e.g., 8b, 32b, 2x16b)
        if len(name_parts) == 3:
            mid = name_parts[1]

            hasDigit = False
            for ch in mid:
                if ch.isdigit():
                    hasDigit = True
                    break

            if not (mid.endswith("b") and hasDigit):
                print("Warning (3.2): Line " + str(i + 1) +
                      " module name '" + module_name +
                      "' has unexpected bitwidth suffix '" + mid + "'\n")

module_name_check(lines)

# Convention 3.3: Module Instance Names
def module_instance_name_check(lines, line_range):

    not_instantiation = ["module", "endmodule", "assign", "always", "always_comb", "always_ff",
                         "wire", "logic", "input", "output", "parameter",
                         "localparam", "begin", "end", "if",
                          "else", "case", "endcase", "for", "while"]

    for i in range(line_range[0], line_range[1]):

        line = lines[i].strip()

        if line == "":
            continue

        if line.startswith("//"):
            continue

        if line.startswith("`"):
            continue

        parts = line.split()
        if len(parts) < 2:
            continue

        type_name     = parts[0]
        instance_name = parts[1]

        # Skip basic non-module instantiation lines
        skip = False
        for w in not_instantiation:
            if type_name == w:
                skip = True
                break
        if skip:
            continue

        # Module names should have uppercases
        if not type_name[0].isupper():
            continue

        # Confirm it's really an instantiation by looking for '(' on this line or next non-empty line
        isInstantiation = False

        # Look if same line has "(" after instance name
        if "(" in line:
            isInstantiation = True
        else:
            # Look if next non-empty line has "("
            j = i + 1
            while j < line_range[1]:
                next_line = lines[j].strip()
                if next_line == "" or next_line.startswith("//"):
                    j = j + 1
                    continue
                if next_line.startswith("("):
                    isInstantiation = True
                break

        if not isInstantiation:
            continue

        # Check for uppercase to check is snake case
        for ch in instance_name:
            if ch.isupper():
                print("Warning (3.3): Line " + str(i + 1) +
                      " module instance name '" + instance_name +
                      "' should use snake_case (lowercase)\n")
                break

        # If the name is long and no underscores, it probably has multiple words 
        if "_" not in instance_name and len(instance_name) > 8:
            print("Warning (3.3): Line " + str(i + 1) +
                  " module instance name '" + instance_name +
                  "' may not be snake_case\n")
            
module_instance_name_check(lines, line_range)

# ------------------------------- #
# Convention 4.X
# ------------------------------- #

# Convention 4.1: GL Allowable Construct Check
def gl_allowable_contruct_check(lines, line_range):
    
    # Not allowed
    disallowed_tokens = [
        "always", "always_comb", "always_ff", "if", "else",
        "case", "endcase", "for", "while", "begin", "end", "logic"
    ]

    # Operators that suggest that assign does computation
    disallowed_ops = ["+", "-", "*", "/", "%", "&", "|",
                      "^", "~", "?", "{", "}", "<<", ">>"]

    for i in range(line_range[0], line_range[1]):

        raw = lines[i]
        line = raw.strip()

        if line == "":
            continue

        if line.startswith("//"):
            continue

        if line.startswith("`"):
            continue

        # Warn on disallowed keywords/tokens
        for token in disallowed_tokens:
            if token in line:
                print("Warning (4.1): Line " + str(i + 1) +
                      " has a disallowed GL construct ('" + token + "')\n")
                break


        # Assign is allowed only for connecting wires or assigning constants
        if line.startswith("assign"):
            for op in disallowed_ops:
                if op in line:
                    print("Warning (4.1): Line " + str(i + 1) +
                          " assign is doing computation (operator '" + op + "')\n")
                    break

gl_allowable_contruct_check(lines, line_range)

# Convention 4.2: GL Signal Decleration
# FIXME: Need to add visual column alignment
def gl_signal_decleration(lines, line_range):
    
    for i in range(line_range[0], line_range[1]):

        raw = lines[i]
        line = raw.strip()

        if line == "":
            continue

        if line.startswith("//"):
            continue

        if line.startswith("`"):
            continue
        parts = line.split()

        if len(parts) == 0:
            continue

        first_word = parts[0]

        if first_word == "wire":

            rest = line[len("wire"):].strip()

            # If first non-space character is not '[' but we see '[' later,
            # then it's an unpacked array like: wire x [8];
            if "[" in rest:

                # If "[" exists, it must come right after wire decleration
                if not rest.startswith("["):
                    print("Warning (4.2): Line " + str(i + 1) +
                          " uses incorrect indexing")
                else:
                    # Check format [N:0]
                    left  = rest.find("[")
                    right = rest.find("]")

                    if right > left:
                        inside = rest[left+1:right].strip()

                        if ":" not in inside:
                            print("Warning (4.2): Line " + str(i + 1) +
                                  " uses incorrect indexing [" + inside + "]\n")
                        else:
                            nums = inside.split(":")
                            if len(nums) == 2:
                                msb = nums[0].strip()
                                lsb = nums[1].strip()

                                if lsb != "0":
                                    print("Warning (4.2): Line " + str(i + 1) +
                                          " uses incorrect indexing [" + inside + "]\n")

gl_signal_decleration(lines, line_range)