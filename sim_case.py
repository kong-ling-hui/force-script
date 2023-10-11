import os
import re
import shutil
import json
from tqdm import tqdm


def sim_case():
    sim_case_json_fp = open('sim_case.json', 'r')
    json_para = json.load(sim_case_json_fp)
    case_folder: str = json_para['case_folder']
    is_spike: bool = json_para['is_spike']
    is_elf: bool = json_para['is_elf']
    sim_cmd_log: str = json_para['sim_cmd_log']

    sim_dir: str = 'sim_'
    spike_cmd: str = 'SPIKE=on'
    elf_cmd: str = 'FORCE_ELF=on'

    # open file
    sim_cmd_log_fp = open(f'{sim_cmd_log}', 'w')

    if not is_spike:
        spike_cmd = ''
        sim_dir = f'{sim_dir}nemu_'
    else:
        sim_dir = f'{sim_dir}spike_'

    if not is_elf:
        elf_cmd = ''
        sim_dir = f'{sim_dir}bin'
    else:
        sim_dir = f'{sim_dir}elf'

    # command
    command = f'bsub -Is make simv_rtl-run {spike_cmd} {elf_cmd} SIM_DIR={sim_dir} RUN_TC='

    for case in tqdm(os.listdir(case_folder)):
        command = f'{command}{case}'
        sim_cmd_log_fp.write(f'{command}\r\n')
        os.system(command)

    sim_cmd_log_fp.close()


if __name__ == '__main__':
    sim_case()
