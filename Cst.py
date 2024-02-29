import os
# 打开并读取文件
file0 = 'gaptraffic-2017-08-03-new'
file = 'saved' + file0
DATA_PATH = "/Users/小巴的工作台/BBS_WORK_SPACE/Python_Workspace/Git-repositories/airport/Datas/DATA"
APT_FILE = os.path.join(DATA_PATH, "tianjin_new.txt")

airc_file_name = "/Users/小巴的工作台/BBS_WORK_SPACE/Python_Workspace/Git-repositories/airport/Datas/traffic/acft_types.txt"

flight_file_name = "/Users/小巴的工作台/BBS_WORK_SPACE/Python_Workspace/Git-repositories/airport/Datas/traffic/" + file0 + ".csv"

# 存储文件的位置

# 确保目录存在
# file = 'saved_figures_gaptraffic-2017-08-19-new'
# os.makedirs(file, exist_ok=True)
