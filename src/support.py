from os import walk
import pygame


def import_folder(path):
    surface_list = []

    # 遍历文件夹
    for _, __, img_files in walk(path):
        # 加载每个素材下的所有图片
        for image in img_files:
            full_path = path + '/' + image
            image_surf = pygame.image.load(full_path).convert_alpha()
            surface_list.append(image_surf)

    return surface_list
