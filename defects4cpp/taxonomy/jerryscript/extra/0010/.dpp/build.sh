python  /home/workspace/tools/build.py \
        --lto=off \
        --unittests=on \
        --jerry-cmdline=off \
        --error-messages=on \
        --snapshot-save=on \
        --snapshot-exec=on \
        --vm-exec-stop=on \
        --vm-throw=on \
        --line-info=on \
        --mem-stats=on \
        --profile=es.next \
        --function-to-string=on \
        --promise-callback=on \
        --builddir=/home/workspace/build/tests/unittests-es.next \
        --install=/home/workspace/build/tests/unittests-es.next/local \
        --compile-flag="$1"

python  /home/workspace/tools/build.py \
        --lto=off \
        --doctests=on \
        --jerry-cmdline=off \
        --error-messages=on \
        --snapshot-save=on \
        --snapshot-exec=on \
        --vm-exec-stop=on \
        --profile=es.next \
        --function-to-string=on \
        --promise-callback=on \
        --builddir=/home/workspace/build/tests/doctests-es.next \
        --install=/home/workspace/build/tests/doctests-es.next/local \
        --compile-flag="$1"

python  /home/workspace/tools/build.py \
        --lto=off \
        --unittests=on \
        --jerry-cmdline=off \
        --error-messages=on \
        --snapshot-save=on \
        --snapshot-exec=on \
        --vm-exec-stop=on \
        --vm-throw=on \
        --line-info=on \
        --mem-stats=on \
        --profile=es5.1 \
        --builddir=/home/workspace/build/tests/unittests-es5.1 \
        --install=/home/workspace/build/tests/unittests-es5.1/local \
        --compile-flag="$1"

python  /home/workspace/tools/build.py \
        --lto=off \
        --doctests=on \
        --jerry-cmdline=off \
        --error-messages=on \
        --snapshot-save=on \
        --snapshot-exec=on \
        --vm-exec-stop=on \
        --profile=es5.1 \
        --builddir=/home/workspace/build/tests/doctests-es5.1 \
        --install=/home/workspace/build/tests/doctests-es5.1/local \
        --compile-flag="$1"

python  /home/workspace/tools/build.py \
        --lto=off \
        --unittests=on \
        --jerry-cmdline=off \
        --error-messages=on \
        --snapshot-save=on \
        --snapshot-exec=on \
        --vm-exec-stop=on \
        --vm-throw=on \
        --line-info=on \
        --mem-stats=on \
        --profile=es5.1 \
        --cmake-param=-DFEATURE_INIT_FINI=ON \
        --builddir=/home/workspace/build/tests/unittests-es5.1-init-fini \
        --install=/home/workspace/build/tests/unittests-es5.1-init-fini/local \
        --compile-flag="$1"

python  /home/workspace/tools/build.py \
        --lto=off \
        --unittests=on \
        --jerry-cmdline=off \
        --error-messages=on \
        --snapshot-save=on \
        --snapshot-exec=on \
        --vm-exec-stop=on \
        --vm-throw=on \
        --line-info=on \
        --mem-stats=on \
        --profile=es5.1 \
        --jerry-math=on \
        --builddir=/home/workspace/build/tests/unittests-es5.1-math \
        --install=/home/workspace/build/tests/unittests-es5.1-math/local \
        --compile-flag="$1"

python  /home/workspace/tools/build.py \
        --clean --debug --compile-flag=-fsanitize=address \
        --compile-flag=-m32 --lto=off --logging=on --line-info=on \
        --error-message=on --system-allocator=on \
        --profile=es2015-subset --stack-limit=20 \
        --compile-flag="$1"
