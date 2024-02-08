file_name = './proj/cpp_peglib/buggy-1/example/calc4.cc'
not_method = ["while", "if", "ifstream", "for", "return"]

def parse_cpp_file(file_name):
    method_dict = {}
    current_method_name = None
    current_method_code = ""
    in_method = False
    num_bracket = 0
    line_num = 0
    begin_line = 0
    end_line = 0

    with open(file_name, 'r') as file:
        for line in file:
            line_num += 1

            if "{" in line:
                num_bracket += 1
            if "}" in line:
                num_bracket -= 1
            if not line.strip().startswith("//") and not line.strip().startswith("#") and not in_method and "(" in line and (line.strip().endswith(")") or line.strip().endswith("\\") or line.strip().endswith("{")) and "=" not in line:
                before_bracket = line.split("(")[0].strip().split()
                if len(before_bracket) < 2:
                    continue
                
                if before_bracket[0] in not_method:
                    continue
                else:
                    in_method = True
                    begin_line = line_num
                    current_method_name = before_bracket[-1]
                    current_method_code += line
            elif in_method and "}" in line and num_bracket == 0:
                current_method_code = current_method_code + line
                end_line = line_num
                method_dict[current_method_name] = {
                    "snippet": current_method_code,
                    "begin_line": begin_line,
                    "end_line": end_line
                }
                in_method = False
                current_method_code = ""
                current_method_name = None

            elif in_method:
                current_method_code += line

            else:
                continue
    return method_dict
              

            
method_dict = parse_cpp_file(file_name)
for method_name in method_dict.keys():
    print("method_name:"+method_name)
    print(type(method_dict[method_name]))
    print("begin_line: ", method_dict[method_name]["begin_line"])
    print("end_line: ", method_dict[method_name]["end_line"])
    print(method_dict[method_name]["snippet"])
    print("==============================================================")

