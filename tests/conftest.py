import sys
from os.path import abspath, dirname, join

root_dir = dirname(dirname(abspath(__file__)))
sys.path.extend([root_dir, join(root_dir, "defects4cpp")])
