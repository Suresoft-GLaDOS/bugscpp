import json

ctags_file = './make_dataset/ctags_result.txt'
try_file = './make_dataset/try.txt'
snippets = []
line_num = 0

with open(ctags_file, 'r') as ctags_file:
    for line in ctags_file:
    # line: main	./proj/cpp_peglib/buggy-1/example/calc.cc	/^int main(void) {$/;"	f	line:8	typeref:typename:int	end:51
        line_num += 1
        
        if("line:" in line):
            pre_line, post_line = line.split("line:")
            pre_line_split = pre_line.split()
            if(pre_line_split[1].startswith('./')):
                func_name = pre_line_split[0]
                file_name = pre_line_split[1]
            elif(pre_line_split[2].startswith('./')):
                func_name = ' '.join(pre_line_split[:2])
                file_name = pre_line_split[2]
            else:
                continue


            post_line_split = post_line.split()
            begin_line = int(post_line_split[0])
            if('end:' in post_line_split[-1]):
                end_line = int(post_line_split[-1].split('end:')[-1])
            else:
                continue
            
            try:
                with open(file_name, 'r') as file:
                    code = file.readlines()
                    snippet = ''.join(code[begin_line-1:end_line])
            except:
                print("error: "+file_name, line_num)
            method = {'func_name': func_name, 'file_name': file_name, 'begin_line': begin_line, 'end_line': end_line, 'snippet': snippet}
            snippets.append(method)

json_file_path = './make_dataset/snippets.json'

with open(json_file_path, 'w') as file:
    json.dump(snippets, file, indent=4, sort_keys=True)



