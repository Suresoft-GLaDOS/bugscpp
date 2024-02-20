files = ['example/calc.cc', 'example/calc2.cc', 'example/calc3.cc', 'example/calc4.cc', 'example/calc5.cc', 'lint/peglint.cc', 'peglib.h', 'test/catch.hh', 'test/test1.cc', 'test/test2.cc', 'test/test3.cc']

directory = './proj/cpp_peglib/buggy-1/'

for file in files:
    file_path = directory+file
    line_num = 0
    with open(file_path, "r") as f:
        for l in f:
            line_num += 1
            if "class" in l:
                print(file)
                print(l)
                print(line_num)