import os
from glob import glob

TARGET_DIR = r"g:\Downloads\蔡规划\琢匠产品"
os.chdir(TARGET_DIR)
files = glob('*.mhtml') + glob('*.html')
print(f'Found {len(files)} files')
for f in files[:5]:
    print(f)
