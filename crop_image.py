import os
import rasterio
from tkinter import Tk, filedialog, simpledialog


def crop_image(image_data, crop_percentage=0.1):
    """
    Crop the image by removing a percentage from each side.
    crop_percentage: float, percentage of the image to remove from all sides (0 < crop_percentage < 0.5).
    """
    # Original dimensions
    height, width = image_data.shape[1], image_data.shape[2]

    # Calculate crop dimensions
    crop_height = int(height * crop_percentage)
    crop_width = int(width * crop_percentage)

    # Ensure dimensions are reasonable after cropping
    if crop_height >= height // 2 or crop_width >= width // 2:
        raise ValueError("Crop percentage too large, results in an empty or too-small image.")

    # Apply cropping
    cropped_image = image_data[:, crop_height:height - crop_height, crop_width:width - crop_width]
    return cropped_image


def crop_tiff(image_path, output_path, crop_percentage=0.1):
    with rasterio.open(image_path) as src:
        profile = src.profile
        image_data = src.read()

    print("Original image data shape:", image_data.shape)

    # Apply cropping
    cropped_image_data = crop_image(image_data, crop_percentage=crop_percentage)
    print("Cropped image data shape:", cropped_image_data.shape)

    # Update profile with new dimensions
    profile.update(height=cropped_image_data.shape[1], width=cropped_image_data.shape[2])

    # Ensure output directory exists and save cropped image
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with rasterio.open(output_path, 'w', **profile) as dst:
        dst.write(cropped_image_data)

    print(f"Cropped TIFF saved as {output_path}")


def select_file_and_crop():
    root = Tk()
    root.withdraw()

    # Select the TIFF file to crop
    image_path = filedialog.askopenfilename(title="Select watermarked TIFF file", filetypes=[("TIFF files", "*.tif")])
    if not image_path:
        print("No TIFF file selected.")
        return

    # Select output directory
    output_directory = filedialog.askdirectory(title="Select Output Directory")
    if not output_directory:
        print("No output directory selected.")
        return

    # Ask user for the crop percentage
    crop_percentage = simpledialog.askfloat("Input Crop Percentage",
                                            "Enter the crop percentage (0 to 0.5):",
                                            minvalue=0, maxvalue=0.5)
    if crop_percentage is None:
        print("No crop percentage entered.")
        return

    # Define output file path
    output_filename = f"cropped_{os.path.basename(image_path)}"
    output_path = os.path.join(output_directory, output_filename)

    # Perform cropping and save the result
    try:
        crop_tiff(image_path, output_path, crop_percentage=crop_percentage)
    except ValueError as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    select_file_and_crop()


