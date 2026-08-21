import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from os import path
from skimage.io import imsave
from skimage.util import img_as_ubyte, img_as_float
from skimage.segmentation import find_boundaries
from skimage.morphology import binary_dilation, disk
from click import progressbar
from rgcode.lib.retina import Retina
from rgcode.lib.unet import Unet
from rgcode.lib.results import Results
from rgcode.lib.settings import recursive
import gc

file_types = (".tif", ".tiff")


def get_file_list(path_list):

    # checks if the input is a single file/folder or a list
    if not isinstance(path_list, list):
        path_list = [path_list]
    

    file_list = []

    # generates a list of paths for later processing
    for folder_path in path_list:

        #folder
        if path.isdir(folder_path):
            # recursive foler
            if recursive is True:
                for root, dirs, files in os.walk(folder_path, topdown=False):
                    for name in files:
                        if name.endswith(file_types):
                            file_path = (os.path.join(root, name))
                            file_list.append(file_path)
            # not recursive
            else:
                for name in os.listdir(folder_path):
                    if name.endswith(file_types):
                        file_path = (os.path.join(folder_path, name))
                        file_list.append(file_path)
        # single file
        else:
            if folder_path.endswith(file_types):
                file_list.append(folder_path)
    
    return file_list


def set_run_parameters(path_list, run_settings, recursive=False, overlay=True):
    try:
        os.mkdir(path.join(run_settings["output_folder"], "output"))
        output_folder = path.join(run_settings["output_folder"], "output")
    except:
        output_folder = path.join(run_settings["output_folder"], "output")

    run_settings["output_folder"] = output_folder

    # gets a list of files to process
    file_list = get_file_list(path_list)

    count_model = Unet(run_settings["count_model_path"])

    seg_model = Unet(run_settings["seg_model_path"])

    if run_settings['csv'] is True:
        results_ext = "csv"
    else:
        results_ext = "xlsx"

    results = Results(path.join(run_settings["output_folder"], f"results.{results_ext}"))

    return output_folder, file_list, count_model, seg_model, results


def process_image(file, count_model, seg_model, results, run_settings, overlay_folder):
    
    if run_settings["resolution"] == 0:
        resolution = None
    else:
        resolution = run_settings["resolution"]
    retina = Retina(file, resolution=resolution)

    retina.blocks, retina.new_shape = retina.get_blocks()

    print("Counting RGCs...")
    count_model.predict(retina, threshold=run_settings["threshold"])

    retina.blocks, retina.new_shape = retina.get_blocks(block_size=512, image_size=(2048, 2048), overlap=0.25, rescale_int=False)

    if run_settings["no_seg"] is False:
        print("Segmenting retina...")
        seg_model.predict(retina, "seg", threshold=run_settings["seg_threshold"], batch_size=4)

    retina.get_properties()
    retina.save_filled_mask(folder=overlay_folder)
    retina.save_centroids(folder=overlay_folder)
    
    angle_val = run_settings.get("user_angle", 45.0)

    fig = retina.make_density_circle_map_fixed_quadrants(
        folder=overlay_folder,
        num_rings=3,
        start_angle=angle_val
    )
    plt.close(fig)
    del fig
    gc.collect()
    results.add_results(retina)

    #REMOVE LATER, ADD ROM SETTINGS
    overlay = True


    savepath = path.join(overlay_folder, retina.filename) + ".tif"
    imsave(savepath, img_as_ubyte(retina.prediction))

    if overlay is True:
        print("Creating overlay")
        overlay = retina.make_overlay()

        savepath = path.join(overlay_folder, retina.filename) + ".jpg"
        print(savepath)

        imsave(savepath, overlay)
    
    if run_settings["exp_seg"] is True:
        print("Exporting mask")
        savepath = path.join(overlay_folder, retina.filename) + "_mask.tif"
        print(savepath)

        imsave(savepath, img_as_ubyte(retina.segmentation))
    
    if run_settings["exp_cent"] is True:
        print("Exporting centroids")
        savepath = path.join(overlay_folder, retina.filename) + "_centroids.csv"

        cent_df = pd.DataFrame(retina.centroids, columns=["Y", "X"])
        cent_df.to_csv(savepath)
    
    if run_settings["isodensity"] is True:

        if run_settings["vector"] is True:
            id_ext = "svg"
        else:
            id_ext = "png"

        savepath = path.join(overlay_folder, retina.filename) + f"_isodensity.{id_ext}"
        # print(savepath)
        print("Creating isodensity map")
        isodensity = retina.make_isodensity(cmap=run_settings["cmap"], bandwidth=run_settings["bandwidth"])
        isodensity.savefig(savepath, dpi=600, pad_inches=0)
    
    return retina


def process_files(path_list, run_settings):

    overlay_folder, file_list, count_model, seg_model, results = set_run_parameters(path_list, run_settings)

    # segmentation
    # seg_model = Unet(r"C:\Users\u0127043\Downloads\09_22_50.370018_model-seg_rbpms.h5")

    # loads files
    for n, file in enumerate(file_list):
        
        print(f"\nProcessing file {n+1} of {len(file_list)}")

        retina = process_image(file, count_model, seg_model, results, run_settings, overlay_folder)


    return file_list

