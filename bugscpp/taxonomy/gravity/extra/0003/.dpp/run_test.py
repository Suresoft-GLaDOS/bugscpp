import subprocess
import sys
import shutil
from pathlib import Path


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python run_test.py [INDEX]")
        sys.exit(1)
    index = int(sys.argv[1])

    root_dir = Path('test/unittest')
    disabled_dir = Path('test/unittest/disabled')
    all_gravity_files = list(root_dir.rglob('*.gravity'))
    all_gravity_files.remove(Path('test/unittest/include_test.gravity'))

    sorted_gravity_files = sorted([f for f in all_gravity_files if disabled_dir not in f.parents])

    # for i, v in enumerate(sorted_gravity_files):
    #     print(i+1, v)

    unittest_dir = Path('unittest_test')
    unittest_dir.mkdir(parents=True, exist_ok=True)

    test_file = sorted_gravity_files[index - 1]
    destination = unittest_dir / test_file.name
    shutil.copyfile(test_file, destination)
    result = subprocess.run(['./unittest', str(unittest_dir)], capture_output=True, text=True)
    ret = 0
    if result.returncode != 0:
        print(f"Failed test {destination}")
        print(result.stdout)
        ret = 1

    shutil.rmtree(unittest_dir)
    exit(ret)
