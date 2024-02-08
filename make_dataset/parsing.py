file_lists = ['example/calc.cc', 'example/calc2.cc', 'example/calc3.cc', 'example/calc4.cc', 'example/calc5.cc', 'lint/peglint.cc', 'peglib.h', 'test/catch.hh', 'test/test1.cc', 'test/test2.cc', 'test/test3.cc']

for file_name in file_lists:
    file_path = ''
    try:
        with open('func_lists.txt', "r") as func_lists:
            for line in func_lists:
                print(line.split())
    except FileNotFoundError:
        print(f"error: '{html_file_name}' is not found")