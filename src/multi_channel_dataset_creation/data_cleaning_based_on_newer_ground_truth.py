import argparse
import os
import csv
import rasterio
import numpy as np

def process_labels(old_labels_dir, new_labels_dir, output_dir, output_csv):
    os.makedirs(output_dir, exist_ok=True)
    tif_files = [f for f in os.listdir(old_labels_dir) if f.endswith(".tif")]
    total_files = len(tif_files)
    results = []

    for idx, filename in enumerate(tif_files, start=1):
        old_path = os.path.join(old_labels_dir, filename)
        new_path = os.path.join(new_labels_dir, filename)
        output_path = os.path.join(output_dir, filename)

        if not os.path.exists(new_path):
            print(f"Skipping {filename}: No corresponding file in new_labels.")
            continue

        with rasterio.open(old_path) as old_src, rasterio.open(new_path) as new_src:
            old_data = old_src.read(1)  # Read as single-band array
            new_data = new_src.read(1)

            mask = (old_data == 1) & (new_data == 2)
            altered_pixels = np.count_nonzero(mask)
            old_data[mask] = 0

            profile = old_src.profile

        with rasterio.open(output_path, 'w', **profile) as dst:
            dst.write(old_data, 1)
            print(f"Processing {idx}/{total_files} images", end='\r')

        results.append((filename, altered_pixels))
    
    print()  # Move to the next line after all processing
    
    # Sort results by number of altered pixels in descending order
    results.sort(key=lambda x: x[1], reverse=True)
    
    # Write results to CSV
    if output_csv:
        with open(output_csv, mode='w', newline='') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(["Filename", "Altered Pixels"])
            writer.writerows(results)
        print(f"Results saved to {output_csv}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--old_labels", required=True, help="Path to folder with old label .tif files")
    parser.add_argument("--new_labels", required=True, help="Path to folder with new label .tif files")
    parser.add_argument("--output", required=True, help="Path to folder where modified .tif files will be saved")
    parser.add_argument("--output_csv", required=True, help="Path to CSV file to store altered pixel counts")
    args = parser.parse_args()

    process_labels(args.old_labels, args.new_labels, args.output, args.output_csv)
