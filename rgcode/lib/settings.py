from os import path

root_dir = path.dirname(path.dirname(path.dirname(path.abspath(__file__))))

recursive = False

default_count_model_path = f"{root_dir}/rgcode/models/count/20200501_20-50-00_rbpms_size-128_split-0.5_batch-32_steps-256_epochs-200_seed-934.h5"
default_seg_model_path = f"{root_dir}/rgcode/models/segmentation/20200512_23-24-23_rbpms-seg_size-512_split-0.15_batch-16_steps-64_epochs-150_seed-3628.h5"

make_overlay = True

default_output_folder = None



