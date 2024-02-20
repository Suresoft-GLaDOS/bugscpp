import re, json

directory = './bugscpp/proj/cpp_peglib/buggy-1/'
not_method = ["while", "if", "ifstream", "for", "return"]
files = ['example/calc.cc', 'example/calc2.cc', 'example/calc3.cc', 'example/calc4.cc', 'example/calc5.cc', 'lint/peglint.cc', 'peglib.h', 'test/catch.hh', 'test/test1.cc', 'test/test2.cc', 'test/test3.cc']
snippets = []
def parse_cpp_file(file_name):
    file = directory + file_name
    if file.startswith('./'):
        src_path = file[2:]
    else:
        src_path = file
        
    if src_path[-3:] in ['.cc', '.hh']:
        class_name = src_path[:-3].replace('/', '.')
    elif src_path[-2:] == '.h':
        class_name = src_path[:-2].replace('/', '.')
    else:
        class_name = src_path.replace('/', '.')
    
    method_dict = {}
    current_method_name = None
    current_method_code = ""
    in_method = False
    in_class = False
    num_bracket = 0
    line_num = 0
    begin_line = 0
    end_line = 0

    with open(file, 'r') as file:
        for line in file:
            line_num += 1
            num_small_bracket = 0

            if "{" in line:
                num_bracket += 1
            if "}" in line:
                num_bracket -= 1
            if line.strip().startswith("class") and "{" in line:
                in_class = True
                current_class_name = line.split()[1]
            elif in_class and "}" in line and num_bracket == 0:
                in_class = False

            if not line.strip().startswith("//") and not line.strip().startswith("#") and not in_method and "(" in line and (line.strip().endswith(")") or line.strip().endswith("\\") or line.strip().endswith("{")) and "else" not in line:
                
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
                    
                    loc_method_name = line.find(current_method_name)
                    end_index = loc_method_name + len(current_method_name)
                    after_method_name = line[end_index:]
                    arguments = ""
                    left_bracket_num = 0
                    right_bracket_num = 0
                    in_argument = False
                    for i in after_method_name:
                        if i == "(" and arguments == "":
                            left_bracket_num += 1
                            in_argument = True
                        elif i == ")":
                            right_bracket_num += 1
                            if (left_bracket_num == right_bracket_num and arguments != ""):
                                arguments += i
                                break
                        if in_argument:
                            arguments += i



            elif not in_class and in_method and "}" in line and num_bracket == 0:
                current_method_code = current_method_code + line
                end_line = line_num
                element = {
                    "src_path": src_path,
                    "class_name": class_name,
                    "signature": class_name + "." + current_method_name + arguments,
                    "snippet": current_method_code,
                    "begin_line": begin_line,
                    "end_line": end_line
                }
                in_method = False
                current_method_code = ""
                current_method_name = None
                snippets.append(element)
            
            elif in_class and in_method and "}" in line and num_bracket == 1:
                current_method_code = current_method_code + line
                end_line = line_num
                element = {
                    "src_path": src_path,
                    "class_name": class_name + "." + current_class_name,
                    "signature": class_name + "." + current_class_name + "." + current_method_name + arguments,
                    "snippet": current_method_code,
                    "begin_line": begin_line,
                    "end_line": end_line
                }
                in_method = False
                current_method_code = ""
                current_method_name = None
                snippets.append(element)

            elif in_method:
                current_method_code += line

            else:
                continue
              

for file in files:
    parse_cpp_file(file)

json_file_path = './autofl/data/bugscpp/cpp_peglib_1/snippet.json'

with open(json_file_path, 'w') as f:
    json.dump(snippets, f, indent = 4)
# for method_name in method_dict.keys():
#     print("method_name:"+method_name)
#     print(type(method_dict[method_name]))
#     print("begin_line: ", method_dict[method_name]["begin_line"])
#     print("end_line: ", method_dict[method_name]["end_line"])
#     print(method_dict[method_name]["snippet"])
#     print("==============================================================")

