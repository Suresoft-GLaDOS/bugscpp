import sys
from os.path import dirname
from os.path import abspath, join
root_dir = join(dirname(dirname(abspath(__file__))), "defects4cpp")
sys.path.append(root_dir)
