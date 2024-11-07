import os
import numpy as np
from PIL import Image
import rasterio
from tkinter import Tk, filedialog


def watermark_embed(pixel_value, static_arg, dynamic_arg):
    n, W = static_arg['n'], static_arg['W']
    pixel_index = dynamic_arg['pixel_index']

    w = W[pixel_index % len(W)]

    # 直接修改最低有效位
    if w == 1:
        return (pixel_value | 1)  # 设置最低位为1
    else:
        return (pixel_value & ~1)  # 清除最低位


def process_pixel_band(band, static_arg):
    processed_band = band.copy()
    for i in range(band.shape[0]):
        for j in range(band.shape[1]):
            pixel_value = int(band[i, j])  # 将像素值转换为整数
            dynamic_arg = {'pixel_index': i * band.shape[1] + j}
            processed_band[i, j] = watermark_embed(pixel_value, static_arg, dynamic_arg)
    return processed_band


def embed_tif(image_path, watermark_path, output_path):
    # 打开图像文件
    with rasterio.open(image_path) as src:
        profile = src.profile
        image_data = src.read()

    print("Image data shape:", image_data.shape)

    # 读取水印并转换为列表
    watermark = np.array(Image.open(watermark_path).convert('1')).astype(int)
    watermark = list(watermark.flatten())
    n = 1  # 使用最低有效位
    static_arg = {'n': n, 'W': watermark}

    # 初始化处理后的图像数据
    processed_image_data = np.empty_like(image_data)

    # 逐个波段处理
    for band in range(image_data.shape[0]):
        processed_image_data[band, :, :] = process_pixel_band(image_data[band, :, :], static_arg)

    print("Processed image data sample:", processed_image_data[:, :5, :5])

    # 确保数据类型与 profile 匹配
    processed_image_data = processed_image_data.astype(profile['dtype'])

    # 创建输出目录（如果不存在）
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # 写入 TIFF 文件
    try:
        with rasterio.open(output_path, 'w', **profile) as dst:
            dst.write(processed_image_data)
        print("Watermarked TIFF saved as", output_path)
    except Exception as e:
        print("Error during saving TIFF file:", e)


def select_files_and_embed():
    # 初始化 Tkinter 并隐藏窗口
    root = Tk()
    root.withdraw()

    # 选择 TIFF 文件
    image_path = filedialog.askopenfilename(title="Select TIFF file", filetypes=[("TIFF files", "*.tif")])
    if not image_path:
        print("No TIFF file selected.")
        return

    # 选择水印文件
    watermark_path = filedialog.askopenfilename(title="Select Watermark file",
                                                filetypes=[("Image files", "*.png;*.jpg;*.jpeg")])
    if not watermark_path:
        print("No watermark file selected.")
        return

    # 选择输出目录
    output_directory = filedialog.askdirectory(title="Select Output Directory")
    if not output_directory:
        print("No output directory selected.")
        return

    # 定义输出文件路径
    output_filename = f"watermarked_{os.path.basename(image_path)}"
    output_path = os.path.join(output_directory, output_filename)

    # 嵌入水印并保存
    embed_tif(image_path, watermark_path, output_path)


if __name__ == "__main__":
    select_files_and_embed()
