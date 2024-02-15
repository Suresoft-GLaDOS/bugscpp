# in bugscpp dir

FILE_LIST=(
example/calc.cc 
example/calc2.cc 
example/calc3.cc 
example/calc4.cc 
example/calc5.cc 
lint/peglint.cc 
peglib.h
test/catch.hh
test/test1.cc
test/test2.cc
test/test3.cc
)
result=""
DATA_DIR=./proj/cpp_peglib/buggy-1/
for FILE_NAME in ${FILE_LIST[@]}; do
    # 명령어 실행하고 그 결과 cmd에 저장
    output=$(ctags --fields=+ne -o - --sort=no ${DATA_DIR}${FILE_NAME})
    result="$result\n$output"
done

echo -e "$result" > ./make_dataset/ctags_result.txt
