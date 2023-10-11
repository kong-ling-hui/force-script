import os
import json
import shutil
import re
import time
import random
# from goto import with_goto


def gen_case():
    # json file parser
    json_file = open('gen_case.json', 'r')
    json_para: dict = json.load(json_file)

    case_folders: list = json_para["case_folders"]
    des_folder: str = json_para["des_folder"]
    repetitions_percase: int = json_para["repetitions_percase"]
    seed: int = json_para["seed"]
    cp_folder: str = json_para["cp_folder"]
    elffile_name: str = json_para["elffile_name"]
    elffile_path: str = json_para["elffile_path"]
    config_file: str = json_para["config_file"]
    force_dir = json_para["force_dir"]
    clear_des_folder: bool = json_para["clear_des_folder"]
    err_cases: str = json_para["err_cases"]
    gen_command: str = json_para["gen_command"]
    percase_pass_rate: str = json_para["percase_pass_rate"]
    elf_s: str = json_para["elf_s"]
    fail_log: str = json_para["fail_log"]

    # get current time stamp
    now = time.strftime("%Y%m%d%H%M%S", time.localtime(int(time.time())))
    # clear des_folder
    if clear_des_folder:
        if os.path.exists(des_folder):
            os.system(f'rm -rf des_folder/*')

    # create destination folder and switch dir
    if not os.path.exists(des_folder):
        print(f'create destination folder: {des_folder}')
        os.makedirs(des_folder)
    os.chdir(des_folder)

    # fen_case_log
    gen_case_log_fp = open('gen_case.log', 'w+')

    elffile_name_fp = open(f'{elffile_name}_{now}.list', 'w+')
    elffile_path_fp = open(f'{elffile_path}_{now}.list', 'w+')
    os.mkdir(f'{elf_s}_{now}')
    os.mkdir(f'{fail_log}_{now}')

    # pass rate
    percase_pass_rate_fp = open(f'{percase_pass_rate}_{now}.list', 'w+')

    # record generate case command
    gen_command_fp = open(f'{gen_command}_{now}.list', 'w+')

    # record generate failed case name
    err_case_fp = open(f'{err_cases}_{now}.list', "w+")

    # get current time and write to err_case.list

    err_case_fp.writelines('###################\r\n')
    err_case_fp.writelines(f'time: {now}\r\n')
    err_case_fp.writelines('###################\r\n')

    if not os.path.exists(cp_folder):
        os.makedirs(cp_folder)

    # seed
    if seed == "":
        seed = random.randint(1, 10000)

    print(f"switch current work dir: {des_folder}")
    print(f"current work dir: {os.getcwd()}")

    # # create case folder in des_folder
    # print("create case folder:")
    # for case_folder in case_folders:
    #     if not os.path.exists(case_folder):
    #         print(f"case_folder: {case_folder} has been created")

    #         os.mkdir(case_folder)
    #     else:
    #         print(f'case_folder: {case_folder} has already exit')

    # generate command
    for case_folder in case_folders:
        for case_file in os.listdir(case_folder):
            print(f'{case_file}###############\r\n')
            if case_file.endswith('py') and not case_file.startswith('_'):
                fail_count = 0
                for _ in range(0, repetitions_percase):

                    # random seed
                    seed = random.randint(0, 100000000)

                    print(f'##################{case_file[0 : -3]}_0x{str(seed)}.log\r\n')
                    command = f'{force_dir}/bin/friscv -t {os.path.join(case_folder, case_file)} -c {os.path.join(force_dir, config_file)} -s 0x{seed} -w -l trace -o handlers_set=Fast > {case_file[0 : -3]}_0x{str(seed)}.log 2>&1 '
                    os.system(command)
                    print(f'command : {command}\r\n')
                    log_fp = open(f'{case_file[0 : -3]}_0x{str(seed)}.log', 'r+')
                    log_content = log_fp.read()
                    find_ret = log_content.find('fail')
                    log_fp.write(command)
                    gen_command_fp.write(f'{command}\r\n')

                    # case generate failed stop loop
                    if find_ret != -1:
                        print(f'failed case: {case_file[0 : -3]}_0x{str(seed)}.log\r\n')
                        err_case_fp.writelines(f'{case_file[0 : -3]}_0x{str(seed)}.log\r\n')
                        fail_count += 1
                        if fail_count >= repetitions_percase / 2:
                            log_fp.write("error rate > 50%, stop generate\r\n")
                            log_fp.close()
                            break
                        else:
                            log_fp.close()
                        continue
                    else:
                        log_fp.close()

                    elffile_name_fp.write(f'{case_file[0 : -3]}_0x{str(seed)}.Default.ELF\r\n')
                    elffile_path_fp.write(f'{des_folder}/{elf_s}_{now}/{case_file[0: -3]}_0x{str(seed)}.Default.ELF\r\n')

                    # copy .log file
                    if os.path.isfile(f'{case_file[0 : -3]}_0x{str(seed)}.log'):
                        os.remove(f'{case_file[0 : -3]}_0x{str(seed)}.log')
                        print(f'remove {case_file[0 : -3]}_0x{str(seed)}.log success\r\n')

                    # copy case_file to cp_folder
                    if cp_folder != "":
                        print(f'#############copy {case_file[0: -3]}_0x{str(seed)}.Default.ELF')
                        shutil.copy(f'{case_file[0: -3]}_0x{str(seed)}.Default.ELF', cp_folder)

                percase_pass_rate_fp.write(f'{case_file} pass rate {repetitions_percase - fail_count}/{repetitions_percase}\r\n')
                    # try:
                    #     # copy case_file to cp_folder
                    #     print(f'#############move {case_file[0: -3]}_0x{str(seed)}.Default.ELF')
                    #     shutil.move(f'{case_file[0: -3]}_0x{str(seed)}.Default.ELF', cp_folder)
                    # except Exception:
                    #     err_case_fp.writelines(f'{case_file}\r\n')
                    #     break

    os.system(f'mv *.log {fail_log}_{now}')
    os.system(f'mv *.ELF {elf_s}_{now}')
    os.system(f'mv *.S {elf_s}_{now}')

    err_case_fp.close()
    gen_command_fp.close()
    percase_pass_rate_fp.close()
    elffile_path_fp.close()
    elffile_name_fp.close()
    json_file.close()


if __name__ == '__main__':
    gen_case()
