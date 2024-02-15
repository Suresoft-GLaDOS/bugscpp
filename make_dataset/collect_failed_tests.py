import os

pre_path = './bugscpp/results/cpp_peglib_1/'
dir_list = os.listdir(pre_path)
# print(dir_list)
wf = open('./autofl/data/bugscpp/cpp_peglib_1/failing_tests', 'w')
for dir in dir_list:
    num = dir.split('-')[-1]
    file_name = num+".test"
    # print(file_name)
    with open(os.path.join(pre_path, dir, file_name)) as f:
        for l in f:
            if l == "failed":
                print(file_name)
                outfile = num+".output"
                with open(os.path.join(pre_path, dir, outfile)) as rf:
                    
                    for l in rf:
                        wf.write(l)
                wf.write('End\n')
                
wf.close()

