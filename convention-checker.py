# Verilog coding convention checker for ECE 2300
# Author: Kaan Akan
# Date  : Feb 5, 2026

import re

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
        if "module" in line and not inModuleDeclaration:
            inModuleDeclaration = True

        if inModuleDeclaration and ";" in line:
            start = i + 1
            inModuleDeclaration = False

        if "endmodule" in line:
            end = i

    return [start, end]

def detect_design_type(lines):

    for line in lines:
        stripped = line.strip()

        if stripped.startswith("module"):
            rest = stripped[len("module"):].strip()
            name = rest.replace("(", " ").replace(";", " ").split()
            if len(name) > 0:
                if name[0].endswith("_GL"):
                    return "GL"
                if name[0].endswith("_RTL"):
                    return "RTL"

        if stripped.startswith("always_comb") or stripped.startswith("always_ff"):
            return "RTL"

    return ""

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
    prevCodeLine = ""
    prevWasContinuation = False

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

        # Continuation lines (e.g., broken-up gate instantiations).
        prevStripped = prevCodeLine.strip()
        isContinuationLine = False
        if prevStripped != "":
            if prevStripped.endswith(","):
                isContinuationLine = True
            elif ("(" in prevStripped and
                  prevStripped.count("(") > prevStripped.count(")") and
                  not prevStripped.endswith(";")):
                isContinuationLine = True

        # Must be indented at least one level inside module
        if currIndent < 2 and not isContinuationLine:
            print("Warning (2.2): Line " + str(i + 1) +
                  " is not indented inside module\n")

        # Allow flexible alignment on continuation lines.
        if currIndent % 2 != 0 and not isContinuationLine:
            print("Warning (2.2): Line " + str(i + 1) +
                  " has inconsistent indentation (" +
                  str(currIndent) + " leading spaces)\n")

        if (abs(prevIndent - currIndent) > 2) and not isContinuationLine and not prevWasContinuation:
            print("Warning (2.2): Line " + str(i + 1) +
                  " may have inconsistent indentation (" +
                  str(currIndent) + " leading spaces)")
            print("Check if line " + str(i + 1) +
                  " is or comes after a continuation\n" )
            
        prevIndent = currIndent
        prevCodeLine = line.split("//")[0]
        prevWasContinuation = isContinuationLine

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
                      "' should use snake case\n")
                break
            break

        # If the name is long and no underscores, it probably has multiple words 
        if "_" not in instance_name and len(instance_name) > 8:
            print("Warning (3.3): Line " + str(i + 1) +
                  " module instance name '" + instance_name +
                  "' should use snake_case\n")
            
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

# Convention 4.3: Primitive Gate Instantiation Check
def primitive_gate_instantiation_check(lines, line_range):

    primitive_gates = ["and", "or", "nand", "nor", "xor", "xnor", "not", "buf"]

    i = line_range[0]
    while i < line_range[1]:

        line = lines[i].split("//")[0].strip()

        if line == "":
            i = i + 1
            continue

        if line.startswith("`"):
            i = i + 1
            continue

        gate_found = False
        for gate in primitive_gates:
            if line.startswith(gate + "(") or line.startswith(gate + " ("):
                gate_found = True
                break

        if not gate_found:
            i = i + 1
            continue

        # Collect full gate statement so multi-line gate declarations are handled.
        stmt = line
        j = i
        while ";" not in stmt and j + 1 < line_range[1]:
            j = j + 1
            next_line = lines[j].split("//")[0].strip()
            if next_line == "":
                continue
            stmt = stmt + " " + next_line

        if ";" not in stmt:
            i = j + 1
            continue

        left = stmt.find("(")
        right = stmt.rfind(")")
        if left != -1 and right != -1 and right > left:
            inside = stmt[left + 1:right]

            bad_spacing = False
            for k in range(0, len(inside)):
                if inside[k] == ",":
                    # Must have at least one space after every comma.
                    if k + 1 >= len(inside) or inside[k + 1] not in [" ", "\t"]:
                        bad_spacing = True
                        break

            if bad_spacing:
                print("Warning (4.3): Line " + str(i + 1) +
                      " has insufficient horizontal whitespace between gate wires\n")

            # If space is used after '(' then it should also be used before ')'
            # (and vice versa) to keep spacing consistent.
            has_space_after_open = len(inside) > 0 and inside[0] in [" ", "\t"]
            has_space_before_close = len(inside) > 0 and inside[-1] in [" ", "\t"]
            if has_space_after_open != has_space_before_close:
                print("Warning (4.3): Line " + str(i + 1) +
                      " has inconsistent whitespace around parentheses\n")

        i = j + 1

# Convention 4.4: GL Literal Check
def gl_literal_check(lines, line_range):

    separators = " \t,;(){}[]=:+-*/%&|^!<>?\n"

    def split_tokens(text):
        tokens = []
        token = ""
        token_start = -1
        idx = 0
        for ch in text:
            if ch in separators:
                if token != "":
                    tokens.append([token, token_start, idx - 1])
                    token = ""
                    token_start = -1
            else:
                if token == "":
                    token_start = idx
                token = token + ch
            idx = idx + 1
        if token != "":
            tokens.append([token, token_start, idx - 1])
        return tokens

    for i in range(line_range[0], line_range[1]):
        line = lines[i].split("//")[0]
        if line.strip() == "":
            continue

        for token_entry in split_tokens(line):
            token = token_entry[0]
            start = token_entry[1]
            end = token_entry[2]

            prev_ch = line[start - 1] if start > 0 else ""
            next_ch = line[end + 1] if end + 1 < len(line) else ""

            # Warn on unsized decimal literals (e.g., 0, 1, 0100, 42).
            if token.isdigit():
                # Ignore bit/part-select indices such as in[3] or bus[7:0].
                if prev_ch == "[" or next_ch == "]":
                    continue
                print("Warning (4.4): Line " + str(i + 1) +
                      " uses unsized literal '" + token +
                      "'; specify bitwidth\n")
                continue

            # For long binary literals, recommend underscores for readability.
            quote_pos = token.find("'")
            if quote_pos <= 0 or quote_pos + 2 > len(token):
                continue

            base_char = token[quote_pos + 1]
            if base_char not in ["b", "B"]:
                continue

            digits = token[quote_pos + 2:]
            if digits == "":
                continue

            has_underscore = "_" in digits
            bit_count = len(digits.replace("_", ""))

            if bit_count >= 8 and not has_underscore:
                print("Warning (4.4): Line " + str(i + 1) +
                      " long binary literal '" + token +
                      "' should use underscores for readability\n")

# Convention 4.5: GL Assign Statement Check
def gl_assign_statement_check(lines, line_range):

    for i in range(line_range[0], line_range[1]):

        line = lines[i].split("//")[0].strip()

        # Do not declare and assign a wire in one statement.
        if line.startswith("wire") and "=" in line:
            print("Warning (4.5): Line " + str(i + 1) +
                  " should not declare and assign a wire in one statement\n")

        # Assign statements should not use concatenation.
        if line.startswith("assign"):
            if "{" in line or "}" in line:
                print("Warning (4.5): Line " + str(i + 1) +
                      " uses concatenation in assign; write explicit bit-level assignments\n")

# Convention 4.6: GL Module Definition Check
def gl_module_definition_check(lines):

    module_count = 0

    i = 0
    while i < len(lines):
        line = lines[i].split("//")[0].strip()
        if not line.startswith("module"):
            i = i + 1
            continue

        module_count = module_count + 1

        parts = line.replace("(", " ").replace(";", " ").split()
        if len(parts) >= 2 and not parts[1].endswith("_GL"):
            print("Warning (4.6): Line " + str(i + 1) +
                  " GL module name '" + parts[1] + "' should end with '_GL'\n")

        if "(" in line:
            print("Warning (4.6): Line " + str(i + 1) +
                  " module opening parenthesis should be on its own line\n")

        j = i + 1
        while j < len(lines) and lines[j].split("//")[0].strip() == "":
            j = j + 1
        if j >= len(lines) or lines[j].split("//")[0].strip() != "(":
            print("Warning (4.6): Line " + str(i + 1) +
                  " expected '(' on its own line after module name\n")
            i = i + 1
            continue

        wire_col = -1
        name_col = -1
        j = j + 1
        while j < len(lines):
            raw = lines[j].split("//")[0].rstrip("\n")
            stripped = raw.strip()
            if stripped == "":
                j = j + 1
                continue

            if stripped == ")" or stripped == ");":
                if stripped != ");":
                    print("Warning (4.6): Line " + str(j + 1) +
                          " module closing line should be ');'\n")
                break

            if len(raw) - len(raw.lstrip(" ")) != 2:
                print("Warning (4.6): Line " + str(j + 1) +
                      " port declaration should be indented by two spaces\n")

            tokens = stripped.rstrip(",").split()
            if len(tokens) < 3 or tokens[0] not in ["input", "output"] or "wire" not in tokens:
                print("Warning (4.6): Line " + str(j + 1) +
                      " malformed port declaration\n")
                j = j + 1
                continue

            if stripped.count(",") > 1:
                print("Warning (4.6): Line " + str(j + 1) +
                      " should declare one port per line\n")

            curr_wire_col = raw.find("wire")
            if wire_col == -1:
                wire_col = curr_wire_col
            elif curr_wire_col != wire_col:
                print("Warning (4.6): Line " + str(j + 1) +
                      " wire keywords are not vertically aligned\n")

            port_name = tokens[-1]
            curr_name_col = raw.rfind(port_name)
            if name_col == -1:
                name_col = curr_name_col
            elif curr_name_col != name_col:
                print("Warning (4.6): Line " + str(j + 1) +
                      " port names are not vertically aligned\n")

            j = j + 1

        i = j + 1

    if module_count > 1:
        print("Warning (4.6): File contains " + str(module_count) +
              " module definitions; expected one top-level GL module\n")

# Convention 4.7: GL Module Instantiation Check
def gl_module_instantiation_check(lines, line_range):

    non_instance_heads = ["module", "endmodule", "assign", "always",
                          "always_comb", "always_ff", "wire", "logic",
                          "input", "output", "parameter", "localparam",
                          "begin", "end", "if", "else", "case", "endcase"]

    i = line_range[0]
    while i < line_range[1]:
        raw = lines[i].split("//")[0].rstrip("\n")
        line = raw.strip()

        parts = line.split()
        if len(parts) < 2 or line == "" or line.startswith("`"):
            i = i + 1
            continue

        module_type = parts[0]
        if module_type in non_instance_heads:
            i = i + 1
            continue
        if not module_type[0].isupper():
            i = i + 1
            continue

        if not module_type.endswith("_GL"):
            print("Warning (4.7): Line " + str(i + 1) +
                  " GL design should only instantiate _GL modules\n")

        base_indent = len(raw) - len(raw.lstrip(" "))
        expected_port_indent = base_indent + 2

        if "(" in line:
            print("Warning (4.7): Line " + str(i + 1) +
                  " opening parenthesis should be on its own line\n")

        j = i + 1
        while j < line_range[1] and lines[j].split("//")[0].strip() == "":
            j = j + 1
        if j >= line_range[1] or lines[j].split("//")[0].strip() != "(":
            print("Warning (4.7): Line " + str(i + 1) +
                  " expected '(' on its own line after module instantiation\n")
            i = i + 1
            continue

        k = j + 1
        paren_entries = []
        while k < line_range[1]:
            port_raw = lines[k].split("//")[0].rstrip("\n")
            port_stripped = port_raw.strip()

            if port_stripped == "":
                k = k + 1
                continue
            if port_stripped == ")" or port_stripped == ");":
                if port_stripped != ");":
                    print("Warning (4.7): Line " + str(k + 1) +
                          " closing parenthesis should be on its own line as ');'\n")
                break

            if len(port_raw) - len(port_raw.lstrip(" ")) != expected_port_indent:
                print("Warning (4.7): Line " + str(k + 1) +
                      " port connection should be indented by two spaces relative to instance line\n")

            if not port_stripped.startswith(".") or port_stripped.count(",") > 1:
                print("Warning (4.7): Line " + str(k + 1) +
                      " each port connection should be on a separate named-connection line\n")

            curr_paren_col = port_raw.find("(")
            if curr_paren_col != -1:
                paren_entries.append([k, curr_paren_col])
            k = k + 1

        # Use the dominant column so we warn on the true outlier(s).
        if len(paren_entries) >= 2:
            col_counts = {}
            for entry in paren_entries:
                col = entry[1]
                if col in col_counts:
                    col_counts[col] = col_counts[col] + 1
                else:
                    col_counts[col] = 1

            target_col = paren_entries[0][1]
            target_count = col_counts[target_col]
            for col in col_counts:
                if col_counts[col] > target_count:
                    target_col = col
                    target_count = col_counts[col]

            for entry in paren_entries:
                line_idx = entry[0]
                col = entry[1]
                if col != target_col:
                    print("Warning (4.7): Line " + str(line_idx + 1) +
                          " child-port start parentheses are not vertically aligned\n")

        i = k + 1

# ------------------------------- #
# Convention 5.X
# ------------------------------- #

# Convention 5.1: RTL Operator Check
def rtl_operator_check(lines, line_range):

    primitive_gates = ["and", "or", "nand", "nor", "xor", "xnor", "not"]

    for i in range(line_range[0], line_range[1]):
        line = lines[i].split("//")[0].strip()

        if line == "":
            continue

        for gate in primitive_gates:
            if line.startswith(gate + "(") or line.startswith(gate + " ("):
                print("Warning (5.1): Line " + str(i + 1) +
                      " RTL should use operators/always blocks, not primitive gate instantiation\n")
                break

# Convention 5.2: RTL Signal Declaration Check
def rtl_signal_declaration_check(lines, line_range):

    for i in range(line_range[0], line_range[1]):
        line = lines[i].split("//")[0].strip()

        if line == "":
            continue

        if line.startswith("wire") or line.startswith("reg"):
            print("Warning (5.2): Line " + str(i + 1) +
                  " RTL should use 'logic' only (not wire/reg)\n")

# ------------------------------- #
# Convention 6.X
# ------------------------------- #

# Convention 6.1: ASCII Character Check
def comment_ascii_character_check(lines):

    for i in range(0, len(lines)):
        line = lines[i]
        if "//" not in line:
            continue

        comment = line.split("//", 1)[1]
        try:
            comment.encode("ascii")
        except UnicodeEncodeError:
            print("Warning (6.1): Line " + str(i + 1) +
                  " comment contains non-ASCII characters\n")

# Convention 6.2: Comment Style Check
def comment_style_check(lines, line_range):

    for i in range(line_range[0], line_range[1]):
        line = lines[i]

        # Do not use block comments.
        if "/*" in line or "*/" in line:
            print("Warning (6.2): Line " + str(i + 1) +
                  " should use '//' comments instead of block comments\n")

        # If // is used, require a space immediately after it.
        comment_start = line.find("//")
        if comment_start == -1:
            continue

        after = line[comment_start + 2:]
        if after == "" or after == "\n":
            continue

        if not after.startswith(" "):
            print("Warning (6.2): Line " + str(i + 1) +
                  " should include a space after '//'\n")

# Convention 6.6: Instructor Comment Check
def instructor_comment_preservation_check(lines):

    instructor_markers = ["LAB ASSIGNMENT", "'''''''''''''''''''''''''"]
    
    for i in range(0, len(lines)):
        line = lines[i]
        if "//" not in line:
            continue

        body = line.split("//", 1)[1].upper()
        for marker in instructor_markers:
            if marker in body:
                print("Warning (6.6): Line " + str(i + 1) +
                      " still contains instructor comments\n")
                break
            break

def run_gl_checks(lines, line_range):

    gl_allowable_contruct_check(lines, line_range)
    gl_signal_decleration(lines, line_range)
    primitive_gate_instantiation_check(lines, line_range)
    gl_literal_check(lines, line_range)
    gl_assign_statement_check(lines, line_range)
    gl_module_definition_check(lines)
    gl_module_instantiation_check(lines, line_range)

def run_rtl_checks(lines, line_range):

    rtl_operator_check(lines, line_range)
    rtl_signal_declaration_check(lines, line_range)

def execute():

    line_range  = find_implementation_range(lines)

    line_length_check(lines, line_range)
    indentation_check(lines, line_range)
    vertical_white_space_check(lines, line_range)
    horizontal_white_space_check(lines, line_range)
    port_and_wire_name_check(lines)
    module_name_check(lines)
    module_instance_name_check(lines, line_range)

    design_type = detect_design_type(lines)

    if design_type == "GL":
        run_gl_checks(lines, line_range)
    elif design_type == "RTL":
        run_rtl_checks(lines, line_range)
    else:
        print("Warning: Could not determine design type (expected _GL or _RTL module)\n")

    comment_ascii_character_check(lines)
    comment_style_check(lines, line_range)
    instructor_comment_preservation_check(lines)

execute()
