python  /home/workspace/tools/build.py \
        --lto=off \
        --unittests=on \
        --jerry-cmdline=off \
        --error-messages=on \
        --snapshot-save=on \
        --snapshot-exec=on \
        --vm-exec-stop=on \
        --line-info=on \
        --mem-stats=on \
        --profile=es2015-subset \
        --builddir=/home/workspace/build/tests/unittests-es2015_subset \
        --install=/home/workspace/build/tests/unittests-es2015_subset/local \
        --compile-flag="$1"

python  /home/workspace/tools/build.py \
        --lto=off \
        --unittests=on \
        --jerry-cmdline=off \
        --error-messages=on \
        --snapshot-save=on \
        --snapshot-exec=on \
        --vm-exec-stop=on \
        --line-info=on \
        --mem-stats=on \
        --profile=es2015-subset \
        --debug \
        --builddir=/home/workspace/build/tests/unittests-es2015_subset-debug \
        --install=/home/workspace/build/tests/unittests-es2015_subset-debug/local \
        --compile-flag="$1"

python  /home/workspace/tools/build.py \
        --lto=off \
        --doctests=on \
        --jerry-cmdline=off \
        --error-messages=on \
        --snapshot-save=on \
        --snapshot-exec=on \
        --vm-exec-stop=on \
        --profile=es2015-subset \
        --builddir=/home/workspace/build/tests/doctests-es2015_subset \
        --install=/home/workspace/build/tests/doctests-es2015_subset/local \
        --compile-flag="$1"

python  /home/workspace/tools/build.py \
        --lto=off \
        --doctests=on \
        --jerry-cmdline=off \
        --error-messages=on \
        --snapshot-save=on \
        --snapshot-exec=on \
        --vm-exec-stop=on \
        --profile=es2015-subset \
        --debug \
        --builddir=/home/workspace/build/tests/doctests-es2015_subset-debug \
        --install=/home/workspace/build/tests/doctests-es2015_subset-debug/local \
        --compile-flag="$1"

python  /home/workspace/tools/build.py \
        --lto=off \
        --unittests=on \
        --jerry-cmdline=off \
        --error-messages=on \
        --snapshot-save=on \
        --snapshot-exec=on \
        --vm-exec-stop=on \
        --line-info=on \
        --mem-stats=on \
        --builddir=/home/workspace/build/tests/unittests-es5.1 \
        --install=/home/workspace/build/tests/unittests-es5.1/local \
        --compile-flag="$1"

python  /home/workspace/tools/build.py \
        --lto=off \
        --unittests=on \
        --jerry-cmdline=off \
        --error-messages=on \
        --snapshot-save=on \
        --snapshot-exec=on \
        --vm-exec-stop=on \
        --line-info=on \
        --mem-stats=on \
        --debug \
        --builddir=/home/workspace/build/tests/unittests-es5.1-debug \
        --install=/home/workspace/build/tests/unittests-es5.1-debug/local \
        --compile-flag="$1"

python  /home/workspace/tools/build.py \
        --lto=off \
        --doctests=on \
        --jerry-cmdline=off \
        --error-messages=on \
        --snapshot-save=on \
        --snapshot-exec=on \
        --vm-exec-stop=on \
        --builddir=/home/workspace/build/tests/doctests-es5.1 \
        --install=/home/workspace/build/tests/doctests-es5.1/local \
        --compile-flag="$1"

python  /home/workspace/tools/build.py \
        --lto=off \
        --doctests=on \
        --jerry-cmdline=off \
        --error-messages=on \
        --snapshot-save=on \
        --snapshot-exec=on \
        --vm-exec-stop=on \
        --debug \
        --builddir=/home/workspace/build/tests/doctests-es5.1-debug \
        --install=/home/workspace/build/tests/doctests-es5.1-debug/local \
        --compile-flag="$1"

python  /home/workspace/tools/build.py \
        --lto=off \
        --unittests=on \
        --jerry-cmdline=off \
        --error-messages=on \
        --snapshot-save=on \
        --snapshot-exec=on \
        --vm-exec-stop=on \
        --line-info=on \
        --mem-stats=on \
        --debug \
        --cmake-param=-DFEATURE_INIT_FINI=ON \
        --builddir=/home/workspace/build/tests/unittests-es5.1-debug-init-fini \
        --install=/home/workspace/build/tests/unittests-es5.1-debug-init-fini/local \
        --compile-flag="$1"

python /home/workspace/tools/build.py \
        --profile=es2015-subset \
        --lto=off \
        --error-messages=on \
        --debug \
        --strip=off \
        --logging=on \
        --compile-flag=-fsanitize=address \
        --stack-limit=15 \
        --compile-flag="$1"
