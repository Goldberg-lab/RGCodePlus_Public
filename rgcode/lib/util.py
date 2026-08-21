import os
from os import path
from rgcode.lib.settings import default_count_model_path, default_seg_model_path


def set_model_path(given_path, model_type="count"):

    if given_path == None:
        if model_type == "count":
            model_path = default_count_model_path
        elif model_type == "seg":
            model_path = default_seg_model_path
    else:
        model_path = given_path
    
    print(f"model: {model_path}")
    return model_path


def set_output_path(given_path, default):
    
    if given_path == None or given_path == "":
        print(f"default: {default}")
        output_folder = default
    else:
        output_folder = given_path
    
    return output_folder


def set_cmap(color_map):

    cmap_list = [
        "magma",
        "viridis"
    ]

    default_cmap = cmap_list[0]

    if color_map in cmap_list:
        return color_map
    else:
        return default_cmap