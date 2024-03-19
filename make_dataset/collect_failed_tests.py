import os

pre_path = './bugscpp/results/libchewing_5_with_b/'
dir_list = os.listdir(pre_path)
# print(dir_list)
wf = open('./data/bugscpp/libchewing_5/failing_tests', 'w')
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
                        if l.startswith("    Start "):
                            test_file = l.split(':')[-1].strip() 
                        wf.write(l)
                wf.write('End\n')

wf.write('\nLogfile starts\n')

log_file = './bugscpp/proj/libchewing/buggy-5/build/test/'+test_file+".log"
with open(log_file, encoding = 'utf-8', errors='ignore') as lf:
    for l in lf:
        wf.write(l)       
wf.close()


