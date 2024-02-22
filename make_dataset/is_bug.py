import re, os, json

directory = './bugscpp/bugscpp/taxonomy/cpp_peglib/patch/'
snippet = './autofl/data/bugscpp/cpp_peglib_1/snippet.json'

lines = []

def buggy_lines(path_to_patch):
    
    
    surrounding_line_width = 1
    
    with open(path_to_patch, "r") as f:
        buggy_file, start_line = None, None
        for l in f:
            if l.startswith("+++"):
                buggy_file = l.strip()[6:]
                continue
            m = re.match("^@@ -\d+,\d+ \+(\d+),\d+ @@", l)
            if m:
                start_line = int(m.group(1))
                current_line = start_line
                continue
            if l.rstrip() == "--":
                buggy_file, start_line = None, None
                continue
            
            if buggy_file and "test" not in buggy_file and start_line:
                if l.startswith("-"):
                    # surrounding lines
                    for offset in range(1, surrounding_line_width+1):
                        lines.append((buggy_file, current_line - offset))
                        lines.append((buggy_file, current_line + offset - 1))
                else:
                    if l.startswith("+"):
                        lines.append((buggy_file, current_line))
                    current_line += 1

def find_buggy_method():
    with open(snippet, 'r') as f:
        json_data = json.load(f)
        
        for m in json_data:
            begin_line = m["begin_line"]
            end_line = m["end_line"]
            file_name = m["src_path"].split("/")[-1]
            m["is_bug"] = False

            for line in lines:
                buggy_file, buggy_line = line

                if file_name == buggy_file and buggy_line >= begin_line and buggy_line <= end_line:
                    m["is_bug"] = True
                    print(buggy_file, buggy_line)
    return json_data



path_to_patch = directory + "0001-buggy.patch"
n = 2
while(os.path.exists(path_to_patch)):
    buggy_lines(path_to_patch)
    path_to_patch = directory + "000" + str(n) + "-buggy.patch"
    n += 1

new_snippet = find_buggy_method()

new_snippet_file = './autofl/data/bugscpp/cpp_peglib_1/snippet.json'

with open(new_snippet_file, 'w') as f:
    json.dump(new_snippet, f, indent = 4)
