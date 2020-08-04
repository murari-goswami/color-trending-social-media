# -*- coding: utf-8 -*-

import numpy as np
from PIL import Image, ImageDraw, ImageFont
import skimage.io
from pylab import plt
import base64
import json
import requests
import math
import operator
import collections
import pandas as pd
import csv
import datetime
import matplotlib.pyplot as plt

from tools import *



####analyze picture if color cannot be mapped to palette
def map_color(color, colors, cache, max_dist=500):
    #color (r, g, b)
    #colors {color_name: (r, g, b), ...}
    if color in cache:
        return cache[color]
    dist = max_dist
    color_index = "NA"
    for k, v in colors.items():
        if abs(sum(color) - sum(v)) > 180:
            continue
        if (color_dif(v, color) < dist):
            color_index = k
            dist = color_dif(v, color)
    cache[color] = [color_index, dist]
    return [color_index, dist]

def filter_main_colors(colors, noise_cut_off, max_diff, min_pct, palette):
    #colors: [color_index] by pixel
    color_counts = dict(collections.Counter([x[0] for x in colors]))
    color_dist = defaultdict(list)
    for color, dist in colors:
        color_dist[color].append(dist)
    avg_dist = {}
    for k,v in color_dist.items():
        avg_dist[k] = int(sum(v)/ float(len(v)))

    all_pixels = sum(color_counts.values())
    color_counts = {k: v for k, v in color_counts.items() if v >= all_pixels * noise_cut_off and k != "NA"}
    color_counts_list = [[k, v] for k, v in color_counts.items()]
    color_counts_list = sorted(color_counts_list, key=operator.itemgetter(1), reverse=False)
    print(color_counts_list)

    for i in range(len(color_counts_list)):
        for ii in range(len(color_counts_list) - 1, i, -1):
            color_x = color_counts_list[i]
            color_y = color_counts_list[ii]
            if i != ii and color_dif(palette[color_x[0]], palette[color_y[0]]) < max_diff:
                ratio = color_x[1] / color_y[1]
                if avg_dist[color_y[0]] > avg_dist[color_x[0]] and ratio > 0.5:
                    color_counts[color_x[0]] += color_counts[color_y[0]]
                    del color_counts[color_y[0]]
                    color_counts_list[ii][0] = color_x[0]
                    break
                else:
                    color_counts[color_y[0]] += color_counts[color_x[0]]
                    del color_counts[color_x[0]]
                    break

    print (color_counts)
    #delete not important colors
    acceptable_pixels = sum(color_counts.values())
    #max_color = max(color_counts, key = color_counts.get)
    main_colors = [[k, v] for k, v in color_counts.items() if v >= acceptable_pixels * min_pct]
    main_colors = sorted(main_colors, key=operator.itemgetter(1), reverse=True)
    print(main_colors)
    return main_colors

def viz_main_colors(main_colors, palette):
    #main_colors: [[color_index, count]]
    weights = [x[1] for x in main_colors]
    weights = [round(float(x) / sum(weights), 2) for x in weights]
    image = Image.new('RGB', (100, 350), (255, 255, 255))
    draw = ImageDraw.Draw(image)
    areas = 0
    font = ImageFont.truetype(font_path, 10)
    for i in range(len(main_colors)):
        area = weights[i] * 300
        draw.rectangle([0, areas, 100, (areas + area)], fill = palette[main_colors[i][0]])
        draw.text((0, areas), main_colors[i][0], fill=(0, 0, 0), font=font)
        areas += area
    return image

def save_images(images, path):
    fig = plt.figure()
    for i, image in enumerate(images):
        fig.add_subplot(1, len(images), i + 1)
        plt.imshow(image)
        plt.axis('off')
    plt.savefig(path, bbox_inches='tight')
    plt.close()

def analyze_picture(file_name):
    print ("process image:" + file_name)
    color_palette = color_palette_full
    raw_image = skimage.io.imread(os.path.join(data_path, file_name))
    if len(raw_image.shape) == 2: raw_image = np.stack([raw_image] * 3, axis=-1)
    adjust_image = raw_image.tolist()
    pixels = [item for sublist in adjust_image for item in sublist]

    people_colors = []
    people_viz = []
    color_map_cache = {}
    if len(pixels) >= 1200:
        reduced_pixels = []
        for i in range(0, len(pixels), math.floor(len(pixels) / 1200)):
            if pixels[i][3] > 0:
                reduced_pixels.append(pixels[i])
        all_colors = [map_color(tuple(x[:3]), color_palette, color_map_cache, color_max_dist) for x in reduced_pixels]
        main_colors = filter_main_colors(all_colors, img_noise_cutoff, img_max_diff, 0.05, color_palette)
        filter_main_colors(all_colors, img_noise_cutoff, img_max_diff, img_pct_cutoff, color_palette)
        people_viz.append(viz_main_colors(main_colors, color_palette))
        for c in main_colors:
            people_colors.append([file_name, c[0], c[1]])

        save_images([raw_image] + people_viz, os.path.join(output_path, file_name))
    return people_colors

    #analyze pictures

    for file in os.listdir(data_path):
        color_info = analyze_picture(file)
        with open(os.path.join(output_path, "color_sum.csv"), 'a+', newline = '') as f:
            writer = csv.writer(f)
            for row in color_info:
        time_it(file + " completed")
