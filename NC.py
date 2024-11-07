import os
import sys

import numpy as np
from PIL import Image

script = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # dirname:上一级路径
path = os.path.join(script, 'vector_process')
sys.path.append(path)
from select_file import select_file


def image_to_array(path):
    image = Image.open(path)  # 替换为你的PNG格式二值图像文件路径
    # 转换为NumPy数组
    image_array = np.array(image).astype(int)
    return image_array


def NC(original_watermark, extract_watermark):
    """
    calculate normalized correlation(NC)
    :param original_watermark:
    :param extract_watermark:
    :return:
    """
    if original_watermark.shape != extract_watermark.shape:
        exit('Input vectors must be the same size!')
    elif ~np.all((original_watermark == 0) | (original_watermark == 1)) | ~np.all(
            (extract_watermark == 0) | (extract_watermark == 1)):
        exit('The input must be a binary image logical value image!')

    result = ~(original_watermark ^ extract_watermark)
    return (result == -1).sum() / original_watermark.size


if __name__ == "__main__":
    original_watermark_path = select_file('select the original watermark',
                                          [("watermark file", "*.png *.jpg")])  # 读取PNG图像文件

    original_watermark = image_to_array(original_watermark_path)
    extract_watermark_path = select_file('select the extract watermark', [("watermark file", "*.png *.jpg")])
    extract_watermark = image_to_array(extract_watermark_path)
    print(NC(original_watermark, extract_watermark))

