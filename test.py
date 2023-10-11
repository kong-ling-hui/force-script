import json
import re
from tqdm import tqdm
import time


def test():
    file = open('des_folder/um_choiceMod_02_force_0x8010.log', 'r')
    read_file = file.read()
    print(read_file)


def test02():
    for _ in tqdm(range(0, 100)):
        time.sleep(0.1)


if __name__ == '__main__':
    test02()
