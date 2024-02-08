with open("./make_dataset/func_lists.txt", "r") as func_list:
    for line in func_list:
        if len(line.split()) not in [9, 14]:
            print(len(line.split()), line)

