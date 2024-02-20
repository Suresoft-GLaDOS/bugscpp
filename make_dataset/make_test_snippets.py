import json

TEST_DIR = './bugscpp/proj/cpp_peglib/buggy-1/test/'
test_cases = []

for i in range(1, 4):
    in_tc_snippet = False
    snippet = ""
    # ./bugscpp/proj/cpp_peglib/buggy-1/test/test1.cc
    test_file = TEST_DIR + "test" + str(i) + ".cc"

    class_name = test_file[2:].replace("/", ".")
    if (class_name[-3:] == ".cc"):
        # bugscpp.proj.cpp_peglib.buggy-1.test.test1
        class_name = class_name[:-3]

    line_num = 0
    bracket_num = 0
    
    with open(test_file, "r") as tf:
        for l in tf:
            if "{" in l:
                bracket_num += 1
            if "}" in l:
                bracket_num -= 1
            line_num += 1

            if l.startswith("TEST_CASE("):
                begin_line = line_num
                in_tc_snippet = True
                snippet += l
                explain = l.split("\"")[1].replace(" ", "_")
                tc_signature = class_name + "." + explain + "()"      
            elif in_tc_snippet and "}" in l and bracket_num == 0:
                end_line = line_num
                snippet += l
                in_tc_snippet = False

                element = {"src_path": test_file,
                "class_name": class_name,
                "signature": tc_signature,
                "snippet": snippet,
                "begin_line": begin_line,
                "end_line": end_line}

                test_cases.append(element)
                snippet = ""
            elif in_tc_snippet:
                snippet += l

json_file_path = './autofl/data/bugscpp/cpp_peglib_1/test_snippet.json'

with open(json_file_path, 'w') as f:
    json.dump(test_cases, f, indent = 4)


