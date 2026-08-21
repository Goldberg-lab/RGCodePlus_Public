import click
try:
    from lib.process import get_file_list
except:
    from rgcode.lib import settings
    from rgcode.lib.process import process_files
    from rgcode.lib.util import set_model_path, set_output_path, set_cmap


@click.command()
@click.argument("path", type=click.Path(exists=True))
@click.option("-cm", '--count-model', "count_model", type=click.Path(exists=True), help="Specify a model file for counting")
@click.option("-sm", '--segmentation-model', "seg_model", type=click.Path(exists=True), help="Specify a model file for counting")
@click.option("-t", '--threshold', "threshold", type=float, default=0.99, help="Specify the threshold for the prediction map (default 0.99)")
@click.option("-st", '--segmentation-threshold', "seg_threshold", type=float, default=0.5, help="Specify the threshold for the segmentation map (default 0.5)")
@click.option("-r", '--resolution', "resolution", type=float, default=0, help="Specify the resolution in pixels per µm")
@click.option("-o", '--output', type=click.Path(exists=True), help="Specify an output folder")
@click.option("-ns", '--no-segmentation', "no_seg", default=False, is_flag=True, help="Skip the segmentation step")
@click.option("-es", '--export-segmentation', "exp_seg", default=False, is_flag=True, help="Export the segmentation mask of the retina")
@click.option("-ec", '--export-centroids', "exp_cent", default=False, is_flag=True, help="Export the cell centroid as csv file")
@click.option("-rec", '--recursive', default=False, is_flag=True, help="Look for files also in subdirectories")
@click.option("-ov", '--overlay', default=False, is_flag=True, help="Export an overlay alongside the binary output")
@click.option("-ni", '--no-isodensity', default=False, is_flag=True, help="Don't export an isodensity map of the retinas")
@click.option("-cmap", '--color-map', help="Select the isodensity color map (magma or viridis)")
@click.option("-bw", '--bandwidth', default=100, type=int, help="Specify the bandwidth of the Gaussian kernel (µm)")
@click.option("-svg", '--vector', default=False, is_flag=True, help="Export the isodensity map as Scalable Vector Graphics (SVG)")
@click.option("-c", '--csv', default=False, is_flag=True, help="Export cmap the results as CSV file instead of Excel")
# @click.option("-bw", '--bandwidth', type=int, help="Specify the bandwith of the gaussian kernel used for the isodensity map")
def main(path, count_model, seg_model, threshold, seg_threshold, resolution, output, no_seg, exp_seg, exp_cent, recursive, overlay, color_map, no_isodensity, bandwidth, vector, csv):
    """Counts retinal ganglion cells on retinal wholemounts"""
    import os
    print(os.getcwd())
    print(count_model)
    print(recursive)
    if recursive:
        settings.recursive = True
    else:
        settings.recursive = False
    
    run_settings = {
        "threshold" : threshold,
        "seg_threshold" : seg_threshold,
        "resolution" : resolution,
        "no_seg" : no_seg,
        "exp_seg" : exp_seg,
        "exp_cent" : exp_cent,
        "recursive" : recursive,
        "overlay" : overlay,
        "isodensity" : not no_isodensity,
        "bandwidth" : bandwidth,
        "vector" : vector,
        "csv" : csv
    }
    
    # count_model_path = set_model_path(count_model, "count")
    # seg_model_path = set_model_path(seg_model, "seg")
    # output_folder = set_output_path(output, click.format_filename(path))
    # cmap = set_cmap(color_map)

    run_settings["count_model_path"] = set_model_path(count_model, "count")
    run_settings["seg_model_path"] = set_model_path(seg_model, "seg")
    run_settings["output_folder"] = set_output_path(output, click.format_filename(path))
    run_settings["cmap"] = set_cmap(color_map)

    process_files(click.format_filename(path), run_settings)


# @click.command()
# @click.option('-s', '--string-to-echo')
# def echo(string_to_echo):
#     click.echo(string_to_echo)


if __name__ =="__main__":
    main()