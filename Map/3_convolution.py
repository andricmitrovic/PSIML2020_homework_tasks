import numpy as np
from PIL import Image
from scipy import signal


def choose_factor():

    max_load = [(50, 20), (100, 40), (500, 20), (1000, 40), (3000, 20), (5000, 40)]
    k = 1

    for temp_count, temp_size in max_load:
        if N < temp_count:
            return k
        if N == temp_count and temp_size <= min(W, H):
            return k
        k += 1

    return k


if __name__ == "__main__":

    map_path = input()
    N = int(input())
    W, H = input().split()
    W = int(W)
    H = int(H)

    patches_path = []

    for _ in range(0, N):
        patches_path.append(input().strip())

    down_sampling_factor = choose_factor()
    tmp_w_h = (int(W/down_sampling_factor), int(H/down_sampling_factor))

    map_img = Image.open(map_path)
    map_array = np.array(map_img, dtype='float64')
    map_img = map_img.resize((int(map_array.shape[1]/down_sampling_factor),
                              int(map_array.shape[0]/down_sampling_factor)), resample=Image.NEAREST)
    map_array = np.array(map_img, dtype='float64')

    face = map_array - map_array.mean()

    for patch in patches_path:

        template_img = Image.open(patch)
        template_img = template_img.resize(tmp_w_h, resample=Image.NEAREST)
        template = np.array(template_img, dtype='float64')

        template -= template.mean()
        corr = signal.correlate(face, template, mode='valid', method='auto')

        y, x, _ = np.unravel_index(np.argmax(corr), corr.shape)

        print(x * down_sampling_factor, y * down_sampling_factor)

        template_img.close()

