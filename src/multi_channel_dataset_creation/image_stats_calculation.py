import argparse
import os
import numpy as np
import rasterio

def process_images(folder, divide_by):
    # Initialize variables to track statistics
    max_max_val = float('-inf')
    min_min_val = float('inf')
    max_mean = float('-inf')
    max_std = float('-inf')

    sum_min_vals = 0
    sum_max_vals = 0
    sum_means = 0
    sum_stds = 0
    image_count = 0

    # Loop through all files in the folder
    for filename in os.listdir(folder):
        filepath = os.path.join(folder, filename)

        if not os.path.isfile(filepath):
            continue

        try:
            # Load the image with rasterio
            with rasterio.open(filepath) as src:
                img_array = src.read(1)  # Read the first band

            # Divide data by the specified value
            img_array = img_array / divide_by

            # Calculate statistics
            img_min = img_array.min()
            img_max = img_array.max()
            img_mean = img_array.mean()
            img_std = img_array.std()

            print(f"{filename}: Min={img_min:.2f}, Max={img_max:.2f}, Mean={img_mean:.2f}, Std={img_std:.2f}")

            # Update extreme values
            if img_max > max_max_val:
                max_max_val = img_max
            if img_min < min_min_val:
                min_min_val = img_min
            if img_mean > max_mean:
                max_mean = img_mean
            if img_std > max_std:
                max_std = img_std

            # Accumulate values for overall average
            sum_min_vals += img_min
            sum_max_vals += img_max
            sum_means += img_mean
            sum_stds += img_std

            image_count += 1

        except Exception as e:
            print(f"Error processing {filename}: {e}")

    # Calculate and display final statistics
    if image_count == 0:
        print("No valid images found in the folder.")
        return

    avg_min_val = sum_min_vals / image_count
    avg_max_val = sum_max_vals / image_count
    avg_mean = sum_means / image_count
    avg_std = sum_stds / image_count

    print("\n--- Final Statistics ---")
    print(f"Maximum of Max Values: {max_max_val:.2f}")
    print(f"Minimum of Min Values: {min_min_val:.2f}")
    print(f"Maximum of Mean Values: {max_mean:.2f}")
    print(f"Maximum of Std Values: {max_std:.2f}")
    print("\n--- Overall Averages ---")
    print(f"Average Min Value: {avg_min_val:.2f}")
    print(f"Average Max Value: {avg_max_val:.2f}")
    print(f"Average Mean: {avg_mean:.2f}")
    print(f"Average Std: {avg_std:.2f}")

def main():
    parser = argparse.ArgumentParser(description="Compute image statistics in a folder using rasterio, with optional division.")
    parser.add_argument('--folder', type=str, required=True, help="Path to the folder containing images.")
    parser.add_argument('--divide_by', type=float, default =1.0, help="Value to divide all pixel data by before collecting statistics.")
    args = parser.parse_args()

    if not os.path.exists(args.folder):
        print(f"Error: Folder '{args.folder}' does not exist.")
        return

    process_images(args.folder, args.divide_by)

if __name__ == "__main__":
    main()
