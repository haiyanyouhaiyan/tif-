import os
import numpy as np
from PIL import Image
import rasterio
from tkinter import Tk, filedialog


def watermark_extract(pixel_value, watermark_bits, pixel_index):
    # 提取最低有效位并存储到水印位数组
    w_bit = pixel_value & 1
    watermark_bits[pixel_index % len(watermark_bits)] = w_bit
    # 打印调试信息
    print(f"Pixel index: {pixel_index}, Pixel value: {pixel_value}, Extracted bit: {w_bit}")


def process_extraction_band(band, watermark_length):
    # 初始化一个数组用于保存提取的水印位
    watermark_bits = [0] * watermark_length

    # 遍历波段中的每个像素，提取最低有效位
    pixel_index = 0
    for i in range(band.shape[0]):
        for j in range(band.shape[1]):
            pixel_value = int(band[i, j])  # 将像素值转换为整数
            watermark_extract(pixel_value, watermark_bits, pixel_index)
            pixel_index += 1
    return watermark_bits


def extract_watermark_tif(image_path, output_watermark_path):
    with rasterio.open(image_path) as src:
        image_data = src.read(1)  # 读取第一个波段

    # 定义水印的长度和尺寸
    side_length = 16
    watermark_length = side_length ** 2

    # 处理波段并提取水印位
    watermark_bits = process_extraction_band(image_data, watermark_length)

    # 将提取的位转换为水印图像
    watermark_array = np.array(watermark_bits).reshape((side_length, side_length)) * 255
    watermark_image = Image.fromarray(watermark_array.astype(np.uint8))

    # 保存为1位深度的二值图像
    watermark_image.convert('1').save(output_watermark_path)
    print(f"Extracted watermark saved as {output_watermark_path}")


def select_files_and_extract():
    root = Tk()
    root.withdraw()

    # 选择带水印的TIFF文件
    image_path = filedialog.askopenfilename(title="Select Watermarked TIFF file", filetypes=[("TIFF files", "*.tif")])
    if not image_path:
        print("No TIFF file selected.")
        return

    # 选择输出目录
    output_directory = filedialog.askdirectory(title="Select Output Directory for Extracted Watermark")
    if not output_directory:
        print("No output directory selected.")
        return

    # 设置输出水印文件路径
    output_filename = f"extracted_watermark_{os.path.splitext(os.path.basename(image_path))[0]}.png"
    output_watermark_path = os.path.join(output_directory, output_filename)

    # 提取并保存水印
    extract_watermark_tif(image_path, output_watermark_path)


if __name__ == "__main__":
    select_files_and_extract()
