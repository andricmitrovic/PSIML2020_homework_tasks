import numpy as np
from PIL import Image
from numpy.lib.stride_tricks import as_strided
#import time


def calculate_factor_harcoded():

    bounds = [(50, 20, 1),
              (500, 30, 2),
              (3000, 20, 3),
              (5000, 30, 4)]

    for bound in bounds:
        if N < bound[0]:
            return bound[2]
        if N == bound[0] and max(W, H) <= bound[1]:
            return bound[2]

    return 5


if __name__ == "__main__":

    #start_time = time.time()

    map_path = input()

    map_img = Image.open(map_path).convert("L")
    map_array = np.array(map_img, dtype='float32')

    N = int(input())
    W, H = input().split()
    W = int(W)
    H = int(H)

    patches_path = []

    for _ in range(0, N):
        patches_path.append(input().strip())

    down_sampling_factor = calculate_factor_harcoded()


    tmp_size = (int(W/down_sampling_factor), int(H/down_sampling_factor))

    map_img = map_img.resize((int(map_array.shape[1]/down_sampling_factor),
                              int(map_array.shape[0]/down_sampling_factor)), resample=Image.NEAREST)
    map_array = np.array(map_img, dtype='float32')

    face = map_array

    for patch in patches_path:

        template_img = Image.open(patch).convert("L")
        template_img = template_img.resize(tmp_size, resample=Image.NEAREST)
        template = np.array(template_img, dtype='float32')

        y = as_strided(face,
                       shape=(face.shape[0] - tmp_size[0] + 1,
                              face.shape[1] - tmp_size[1] + 1,) +
                              tmp_size,
                       strides=face.strides * 2)

        ssd = np.einsum('ijkl,kl->ij', y, template, casting='unsafe')
        ssd *= - 2
        ssd += np.einsum('ijkl, ijkl->ij', y, y, casting='unsafe')
        ssd += np.einsum('ij, ij', template, template, casting='unsafe')

        y, x = np.unravel_index(np.argmin(ssd), ssd.shape)
        print(x * down_sampling_factor, y * down_sampling_factor)

        template_img.close()

    #print("--- %s seconds ---" % (time.time() - start_time))
    #print(down_sampling_factor)
