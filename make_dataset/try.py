f1 = './proj/cpp_peglib/buggy-2/test/test1.cc'
f2 = './proj/cpp_peglib/buggy-2/test/test2.cc'
f3 = './proj/cpp_peglib/buggy-2/test/test3.cc'
test_num = 0
with open(f1, 'r') as f:
    for line in f:
        if('TEST_CASE(' in line):
            test_num += 1

with open(f2, 'r') as f:
    for line in f:
        if('TEST_CASE(' in line):
            test_num += 1

with open(f3, 'r') as f:
    for line in f:
        if('TEST_CASE(' in line):
            test_num += 1
print(test_num)