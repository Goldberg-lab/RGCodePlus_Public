from os import path
from tifffile import TiffFile
from skimage.transform import rescale, resize
from skimage.exposure import rescale_intensity
from skimage.measure import label, regionprops
from skimage.draw import circle
from skimage.morphology import binary_dilation, disk, remove_small_objects
from skimage.segmentation import find_boundaries
from skimage.io import imsave, imread
# from matplotlib import rcParams
# from keras_unet.utils import get_patches, plot_patches
from skimage.util import view_as_windows, view_as_blocks, montage, crop, img_as_float, img_as_ubyte
import matplotlib
matplotlib.use('Agg')  # Use non-GUI backend before importing pyplot
import matplotlib.pyplot as plt
plt.ioff()
import seaborn as sns
import matplotlib.cm as cm
import seaborn as sns
import numpy as np
import pandas as pd
import os
from collections import Counter
from matplotlib.cm import ScalarMappable
from matplotlib.colors import Normalize
from tifffile import imsave

class Retina(object):

    def __init__(self, file_path, resolution=None):
        
        # sets some useful shortcuts
        self.full_path = file_path
        self.folder, self.full_filename = path.split(self.full_path)
        self.filename, self.ext = path.splitext(self.full_filename)

        self.resolution = resolution

        # defines the target scale for the model
        self.__target_res = 2.1672 / 2

        # loads in the actual image
        self.load_image()

    def load_image(self):

        print(f"Loading {self.full_filename}")

        # loading the picture and storing the metadata
        with TiffFile(self.full_path) as tif:
            if self.resolution == None:
                self.x_resolution = tif.pages[0].tags['XResolution'].value[0] / 1000000
                self.y_resolution = tif.pages[0].tags['YResolution'].value[0] / 1000000
            else:
                self.x_resolution = self.resolution
                self.y_resolution = self.resolution
            image = img_as_float(tif.asarray())
            image = rescale_intensity(image)
            self.original_image = image

            # rescales to the target scale
            if (np.round(self.x_resolution, decimals=1) != np.round(self.__target_res, decimals=1)) or (np.round(self.y_resolution, decimals=1) != np.round(self.__target_res, decimals=1)):
                image = self.rescale_to_target(image)

            self.image = image
            self.shape = image.shape
            return image
    

    def rescale_to_target(self, image, reverse=False, anti_aliasing=True):

        # calculates rescale factor
        x_rescale_factor = self.__target_res / self.x_resolution
        y_rescale_factor = self.__target_res / self.y_resolution

        # if upscaling take the reciprocal
        if reverse is True:
            x_rescale_factor = 1 / x_rescale_factor
            y_rescale_factor = 1 / y_rescale_factor

        return rescale(image, (x_rescale_factor, y_rescale_factor), anti_aliasing=anti_aliasing)
    

    def get_blocks(self, block_size=128, image_size=None, overlap=0.125, rescale_int=False):

        # gets the image
        if image_size == None:
            img = self.image
        else:
            # img = resize(self.image, image_size)

            img = rescale_intensity(self.image)

            shape = np.array(img.shape)

            ratio = shape.min() / shape.max()

            new_shape = np.copy(shape)
            if shape[0] == shape[1]:
                new_shape = image_size
            else:
                new_shape[shape.argmax()] = image_size[0]
                new_shape[shape.argmin()] = image_size[0] * ratio

            img = resize(img, new_shape)


        # sets measurements

        # 12,5% overlap. Works well with powers of 2
        overlap = int(block_size * overlap)
        step_size = block_size - overlap

        # compansating for overlap. Will remove half of the overlap
        right_pad = int(overlap / 2)
        self.right_pad = right_pad

        # this pads the image so it generates an extra set of blocks on the right with the
        # otherwise missing part of the picture
        shape = np.array(img.shape)
        self.shape = shape
        padded_shape = (np.ceil(shape / step_size) * step_size).astype(int)
        left_pad = padded_shape - shape + overlap + right_pad

        # applies the padding
        img = np.pad(img, pad_width=[(right_pad, left_pad[0]), (right_pad, left_pad[1])], mode='constant', constant_values=0)

        # generates overlapping patches
        blocks = view_as_windows(img, (block_size, block_size), step=step_size)
        new_shape = (blocks.shape[0], blocks.shape[1])

        # flattens to a 3D array
        blocks = np.reshape(blocks, (blocks.shape[0] * blocks.shape[1], blocks.shape[2], blocks.shape[3]))

        if rescale_int is True:
            blocks = np.array([rescale_intensity(block) for block in blocks])

        return blocks, new_shape
    
    def save_centroids(self, filename=None, folder=None):
            if not hasattr(self, 'centroids') or self.centroids is None or len(self.centroids) == 0:
                print("No centroids to save.")
                return None

            df = pd.DataFrame(self.centroids[:, [1, 0]], columns=['x', 'y'])
            if filename is None:
                filename = f"{self.filename}_centroids.csv"
            if folder is not None:
                filepath = os.path.join(folder, filename)
            else:
                filepath = os.path.join(self.folder, filename)

            df.to_csv(filepath, index=False)
            print(f"Centroids saved to {filepath}")
            return filepath

    def save_filled_mask(self, filename=None, folder=None):
        # Use cleaned segmentation mask
        mask = img_as_ubyte(self.segmentation > 0)  

        if filename is None:
            filename = f"{self.filename}_filled_mask.tif"
        if folder is not None:
            filepath = os.path.join(folder, filename)
        else:
            filepath = os.path.join(self.folder, filename)

        imsave(filepath, mask)
        print(f"Filled mask saved to {filepath}")
        return filepath

    def make_density_circle_map_fixed_quadrants(
        self, folder=None, num_rings=3, start_angle=0.0
    ):        

        # Prioritize: user input -> self attribute -> fallback 0.0 (if default doesn't work)
        start_angle = getattr(
            self, 'starting_angle', getattr(self, 'user_angle', start_angle)
        )
        theta_0 = float(start_angle) % 360.0

        print(
            f'Starting fixed-quadrant density map (0° at 12 o\'clock, rotated {theta_0:.1f}° CW)...'
        )

        mask = getattr(self, 'segmentation', getattr(self, 'segmentaton', None))
        if mask is None:
            raise ValueError(
                'No segmentation found on object. Run get_properties() first.'
            )

        height, width = mask.shape
        ys, xs = np.nonzero(mask)

        if (
            not hasattr(self, 'centroids')
            or self.centroids is None
            or len(self.centroids) == 0
        ):
            raise ValueError('No centroids found. Run get_properties() first.')

        # Area per pixel calculation (mm²)
        mask_pixels = np.count_nonzero(mask)
        if mask_pixels == 0:
            raise ValueError('Mask is empty; cannot compute areas.')
        if hasattr(self, 'area') and self.area is not None and self.area > 0:
            pixel_area_mm2 = self.area / mask_pixels
        else:
            x_res = getattr(self, 'x_resolution', 1.0)
            y_res = getattr(self, 'y_resolution', 1.0)
            pixel_area_mm2 = 1.0 / (x_res * y_res * 1_000_000.0)
        print(f'Using pixel_area_mm2 = {pixel_area_mm2:.6e} mm^2/pixel')

        x = self.centroids[:, 1]
        y = self.centroids[:, 0]

        center_x = width // 2
        center_y = height // 2

        max_radius = np.max(np.sqrt((xs - center_x) ** 2 + (ys - center_y) ** 2))
        radii = np.linspace(0, max_radius, num_rings + 1)

        # The angles work as follows: 0° = Top (12 o'clock), rotating clockwise
        Y, X = np.ogrid[:height, :width]
        dist_map = np.sqrt((X - center_x) ** 2 + (Y - center_y) ** 2)
        angle_map = (
            np.degrees(np.arctan2(X - center_x, center_y - Y)) + 360.0
        ) % 360.0

        # Diveider lines rotater
        fixed_bounds = [(theta_0 + k * 90.0) % 360.0 for k in range(5)]
        ring_angle_bounds = {i: fixed_bounds for i in range(num_rings)}

        rgc_coords = np.array(list(zip(x, y)))
        distances = np.sqrt(
            (rgc_coords[:, 0] - center_x) ** 2 + (rgc_coords[:, 1] - center_y) ** 2
        )
        angles = (
            np.degrees(
                np.arctan2(rgc_coords[:, 0] - center_x, center_y - rgc_coords[:, 1])
            )
            + 360.0
        ) % 360.0

        ring_idx = np.digitize(distances, radii) - 1
        ring_idx = np.clip(ring_idx, 0, num_rings - 1)

        # Shift angles relative to theta_0: Quadrant 0 starts at theta_0 and spans 90° CW
        shifted_angles = (angles - theta_0) % 360.0
        sector_idx = (shifted_angles // 90).astype(int)
        sector_idx = np.clip(sector_idx, 0, 3)

        region_ids = list(zip(ring_idx.tolist(), sector_idx.tolist()))

        # Compute region areas in mm² 
        shifted_angle_map = (angle_map - theta_0) % 360.0
        region_areas = {}

        for i in range(num_rings):
            inner_r = radii[i]
            outer_r = radii[i + 1]
            ring_mask = (dist_map >= inner_r) & (dist_map < outer_r) & (mask > 0)

            for q in range(4):
                q_start = q * 90.0
                q_end = (q + 1) * 90.0

                if q == 3:
                    angle_mask = (shifted_angle_map >= q_start) & (
                        shifted_angle_map <= q_end
                    )
                else:
                    angle_mask = (shifted_angle_map >= q_start) & (
                        shifted_angle_map < q_end
                    )

                region_mask = ring_mask & angle_mask
                region_areas[(i, q)] = np.sum(region_mask) * pixel_area_mm2

        # Counts and densities (cells/mm²)
        cell_counts = Counter(region_ids)
        densities = {
            k: (cell_counts.get(k, 0) / area if area > 0 else 0.0)
            for k, area in region_areas.items()
        }

        total_area_mm2 = float(np.sum(list(region_areas.values())))

        # Visualization
        visual = np.zeros((*mask.shape, 3), dtype=np.uint8)
        density_values = np.array(list(densities.values()))
        max_density = np.max(density_values) if density_values.size > 0 else 0.0
        norm_densities = {
            k: (v / max_density if max_density > 0 else 0.0)
            for k, v in densities.items()
        }

        for i in range(num_rings):
            inner_r = radii[i]
            outer_r = radii[i + 1]
            ring_mask = (dist_map >= inner_r) & (dist_map < outer_r) & (mask > 0)

            for q in range(4):
                q_start = q * 90.0
                q_end = (q + 1) * 90.0

                if q == 3:
                    quad_mask = (shifted_angle_map >= q_start) & (
                        shifted_angle_map <= q_end
                    )
                else:
                    quad_mask = (shifted_angle_map >= q_start) & (
                        shifted_angle_map < q_end
                    )

                region_mask = ring_mask & quad_mask
                density_norm = norm_densities.get((i, q), 0.0)
                color = plt.cm.viridis(density_norm)[:3]

                for c in range(3):
                    visual[..., c][region_mask] = (color[c] * 255).astype(np.uint8)

        # Save raw image
        target_folder = folder or getattr(self, 'folder', '.')
        visual_save_path = os.path.join(
            target_folder, f'{self.filename}_density_fixed_quadrants_raw.tif'
        )
        imsave(visual_save_path, visual.astype(np.uint8))
        #print(f'Raw density image saved to {visual_save_path}')

        fig, ax = plt.subplots(figsize=(12, 12))
        ax.imshow(visual)

        # Draw concentric circles
        for r in radii[1:]:
            circ = plt.Circle(
                (center_x, center_y), r, color='white', linestyle='--', fill=False
            )
            ax.add_patch(circ)

        for angle_deg in fixed_bounds[:4]:
            theta = np.radians(angle_deg)
            x0 = center_x + radii[0] * np.sin(theta)
            y0 = center_y - radii[0] * np.cos(theta)
            x1 = center_x + radii[-1] * np.sin(theta)
            y1 = center_y - radii[-1] * np.cos(theta)
            ax.plot([x0, x1], [y0, y1], color='white', linestyle='--', alpha=0.6)

        # Label quadrants at exact rotated midpoints (Top/CW convention)
        for i in range(num_rings):
            inner_r = radii[i]
            outer_r = radii[i + 1]
            mid_r = (inner_r + outer_r) / 2.0

            for q in range(4):
                midpoint_deg = (theta_0 + q * 90.0 + 45.0) % 360.0
                theta_rad_mid = np.radians(midpoint_deg)
                label_x = center_x + mid_r * np.sin(theta_rad_mid)
                label_y = center_y - mid_r * np.cos(theta_rad_mid)

                density_val = densities.get((i, q), 0.0)
                ax.text(
                    label_x,
                    label_y - 15,
                    f'Q{q}\nDensity: {density_val:.2e}',
                    color='white',
                    ha='center',
                    va='bottom',
                    fontsize=6,
                    bbox=dict(boxstyle='round,pad=0.2', fc='black', alpha=0.5),
                )
                count_val = cell_counts.get((i, q), 0)
                ax.text(
                    label_x,
                    label_y + 15,
                    f'Cells: {count_val}',
                    color='white',
                    ha='center',
                    va='top',
                    fontsize=6,
                    bbox=dict(boxstyle='round,pad=0.2', fc='black', alpha=0.5),
                )

        ax.set_title(
            f'Retina Density Map (0° Top, Rotated {theta_0:.1f}° CW)', fontsize=14
        )
        ax.axis('off')

        norm = Normalize(vmin=0, vmax=max_density if max_density > 0 else 1.0)
        sm = ScalarMappable(norm=norm, cmap='viridis')
        sm.set_array([])

        cbar = plt.colorbar(sm, ax=ax, fraction=0.046, pad=0.04)
        cbar.set_label('RGC Density (cells / mm²)', fontsize=12)

        annotated_save_path = os.path.join(
            target_folder, f'{self.filename}_density_fixed_quadrants_annotated.png'
        )
        fig.savefig(annotated_save_path, dpi=100, bbox_inches='tight')
        print(f'Annotated density image saved to {annotated_save_path}')

        self.last_density_visual = visual
        self.save_density_map_results(
            densities, cell_counts, region_areas, total_area_mm2, folder=target_folder
        )
        return fig


    def save_density_map_results(self, densities, cell_counts, region_areas, total_area, folder=None, filename=None):
        import pandas as pd

        # Prepare data for DataFrame
        data = []
        for key in densities:
            ring, quadrant = key
            data.append({
                "Ring": ring,
                "Quadrant": quadrant,
                "Density (cells/mm^2)": densities[key],
                "Cell Count": cell_counts.get(key, 0),
                "Region Area (px)": region_areas[key]
            })

        # Add total area as a summary row
        data.append({
            "Ring": "Total",
            "Quadrant": "",
            "Density (cells/mm^2)": "",
            "Cell Count": sum(cell_counts.values()),
            "Region Area (mm^2)": sum(region_areas.values()),
            "Total Area (mm^2)": total_area
        })

        df = pd.DataFrame(data)

        # Set file path
        if filename is None:
            filename = f"{self.filename}_density_results.xlsx"
        if folder is not None:
            filepath = os.path.join(folder, filename)
        else:
            filepath = os.path.join(self.folder, filename)

        # Save to Excel
        df.to_excel(filepath, index=False)
        print(f"Density map results saved to {filepath}")
        return filepath




    def make_overlay(self):

        # creates an image with dots on the cell's centorids
        dot_image = np.zeros(self.prediction.shape)

        # sets the radius of the dots
        # radius = int(2 * self.x_resolution / self.__target_res)
        radius = int(np.round((4 / 2.17) * self.x_resolution, 0))

        # draws circels centred around the centroids
        for coords in self.centroids:
            rr, cc = circle(coords[0], coords[1], radius, shape=dot_image.shape)
            dot_image[rr, cc] = 1
        
        dot_image = img_as_ubyte(dot_image > 0.5)
        self.dot_image = dot_image

        # creates an empty blue chennel
        blue = np.zeros(self.original_image.shape, dtype=np.ubyte)

        # stacks the pictures in an RGB one
        overlay = np.dstack([self.dot_image, img_as_ubyte(self.original_image), blue])

        # makes a contour of the retina if available
        try:
            self.make_contour()
            overlay = np.maximum(self.contour, overlay)
            self.overlay = img_as_ubyte(overlay)
        except:
            self.overlay = img_as_ubyte(overlay)

        return img_as_ubyte(overlay)
    

    def make_isodensity(self, cmap, bandwidth):

        # TODO set DPI and COLORMAP
        
        # Set maximum density
        max_density = 6000
        cell_count = self.count
        vmax = float(max_density * 10 / cell_count / 10000000)
        n_levels = 12
        # print(f"vmax: {vmax}")


        centroids = self.centroids * (1/self.x_resolution)


        fig, ax = plt.subplots(figsize=(6, 5))
        sns.kdeplot(centroids[:, 1], np.flip(centroids[:, 0]), cbar=False, legend=False, shade=True, shade_lowest=False, cmap=cmap, vmax=vmax, bw=bandwidth, n_levels=n_levels)

        # Sets scalebar converting the probability function to actual density
        scale_max = vmax / 10 * cell_count * 10000000
        ###print("density", scale_max)
        linspace = np.linspace(0, scale_max, n_levels + 1)
        # print(linspace)
        m = plt.cm.ScalarMappable(cmap=cmap)
        m.set_array([0, scale_max])
        m.set_clim(0., scale_max)
        plt.colorbar(m, ticks=np.linspace(0, scale_max, n_levels + 1))
        # fig.axes[1].set_yticklabels(np.linspace(0, max_density * 1.1 , 11, dtype=np.int))

        # Set x,y labels
        label = "Position (µm)"
        fig.axes[0].set_xlabel(label)
        fig.axes[0].set_ylabel(label)

        fig.axes[0].axis('off')

        # Set scale label
        fig.axes[1].set_ylabel("Density (cells/mm$\mathregular{^{2}}$)")

        return fig
    

    def make_contour(self):

        # finds the contour of the retina
        contour = find_boundaries(self.segmentation)
        contour = binary_dilation(contour, selem=disk(5))

        # stacks the contour so it can be blended in an overlay
        white_contour = np.dstack([contour, contour, contour])

        self.contour = img_as_ubyte(white_contour)

        return white_contour
    

    def get_properties(self):

        # clean based on the segmentation, if available
        try:
            # get the toal segmented area
            total_area = np.count_nonzero(self.segmentation)

            # remove objects that are less than 2,5% of the toal area
            area_threshold = total_area * 0.025
            clean_segmentation = remove_small_objects(self.segmentation, min_size=area_threshold)

            # get the area and converts it to mm^2
            self.area = np.count_nonzero(clean_segmentation) * (1/self.x_resolution) * (1/self.y_resolution) / 1000000

            # delete what falls outside of the segmentation
            segmented_prediction = self.prediction
            segmented_prediction[~clean_segmentation] = False
        except:
            segmented_prediction = self.prediction
            clean_segmentation = np.ones(self.probability_map.shape)
            self.area = np.count_nonzero(clean_segmentation) * (1/self.x_resolution) * (1/self.y_resolution) / 1000000

        # labels the binary image and gets objects
        label_image = label(segmented_prediction)
        regions = regionprops(label_image)
        centroids = [region.centroid for region in regions]
        self.centroids = np.array(centroids).astype(int)

        # np.save("centroids.npy", self.centroids)

        # stores the count and overrides prediction and segmentation
        self.count = len(regions)
        self.density = np.round(self.count / self.area, 2)
        self.segmentaton = clean_segmentation
        self.prediction = segmented_prediction

        return self.count

