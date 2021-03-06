import cv2
import numpy as np

kernel_x = np.array([[0., 0., 0.], [-1., 0., 1.], [0., 0., 0.]], dtype=np.float64)
kernel_y_left = np.array([[0., 0., 0.], [0., 0., 1.], [0., -1., 0.]], dtype=np.float64)
kernel_y_right = np.array([[0., 0., 0.], [1., 0., 0.], [0., -1., 0.]], dtype=np.float64)


def calc_energy_map(img):
    b, g, r = cv2.split(img)
    # b_energy = np.absolute(cv2.Scharr(b, -1, 1, 0)) + np.absolute(cv2.Scharr(b, -1, 0, 1))
    # g_energy = np.absolute(cv2.Scharr(g, -1, 1, 0)) + np.absolute(cv2.Scharr(g, -1, 0, 1))
    # r_energy = np.absolute(cv2.Scharr(r, -1, 1, 0)) + np.absolute(cv2.Scharr(r, -1, 0, 1))

    b_energy = np.absolute(cv2.Scharr(b, -1, 1, 0), dtype=np.int16) + np.absolute(cv2.Scharr(b, -1, 0, 1), dtype=np.int16)
    g_energy = np.absolute(cv2.Scharr(g, -1, 1, 0), dtype=np.int16) + np.absolute(cv2.Scharr(g, -1, 0, 1), dtype=np.int16)
    r_energy = np.absolute(cv2.Scharr(r, -1, 1, 0), dtype=np.int16) + np.absolute(cv2.Scharr(r, -1, 0, 1), dtype=np.int16)
    return b_energy + g_energy + r_energy

def calc_neighbor_matrix(img, kernel):
    b, g, r = cv2.split(img)
    output = np.absolute(cv2.filter2D(b, -1, kernel=kernel)) + \
             np.absolute(cv2.filter2D(g, -1, kernel=kernel)) + \
             np.absolute(cv2.filter2D(r, -1, kernel=kernel))
    return output


# @author: Weixiong Lin
def norm(color):
    """Calculate norm of pixel's color.

    Args:
        color: The 3-tuple vector of pixel's color.
    
    Return:
        norm_of_color:
    """
    R, G, B = color[0], color[1], color[2]
    tmp = (R*R + G*G + B*B)**0.5
    # print("temp", int(tmp))
    return int(tmp)

# @author: Weixiong Lin
def branding(img, index, radius):
    """Brand images where we want.

    Assistant function to signify the marks in the figure.

    Args:
        img: Images we want to mark.
        index: Index of brands.
        radius: Radius of brands.
    
    Returns:
        img: Branded image with marks on.
    """
    x, y = index
    dx = [i for i in range(-radius, radius)]
    dy = [i for i in range(-radius, radius)]
    height, width = img.shape
    for i in dx:
        for j in dy:
            if x+i > 0 and x+i < height and y+j > 0 and y+j < width:
                img[x+i, y+j] = 255
    return img

# @author: Weixiong Lin
def max_width(mask):
    """Calculate maximum width of the mask area

    Scan row by row of the mask image.

    Args:
        mask: The path of mask image.
    
    Returns:
        max_width_mask: The maximum width of mask area.
    
    Raises:
        FileError: An error occured accessing the image object.
    """
    # mask_img = cv2.imread(mask, cv2.IMREAD_GRAYSCALE)
    mask_img = mask
    # cv2.imwrite("mask_img.jpg", mask_img)
    # print("pixel:", mask[0, 0])
    ret, mask_img = cv2.threshold(mask_img, 30, 255, cv2.THRESH_BINARY)
    # print("shape", mask_img.shape)
    height, width = mask_img.shape

    # count max width
    max_wid = 0
    for i in range(height):
        # initialize leftend and rightend of mask area as -1
        leftend = -1
        rightend = -1
        for j in range(width-1):
            if mask_img[i, j] > 127 and leftend == -1:
                leftend = j
            if mask_img[i, j] == 0 and mask_img[i, j-1] > 0 and j > 0:
                rightend = j
                cv2.imwrite("mask_img.png", branding(mask_img, (i, j), 1))
                print("leftend:({}, {}); rightedn:({}, {})\n".format(i, leftend, i, rightend))
                break
        max_wid = max(max_wid, rightend-leftend)
    # for col in range(width):
    #     # initialize leftend and rightend of mask area as -1
    #     leftend = -1
    #     rightend = -1
    #     for row in range(height-1):
    #         if mask_img[row, col] > 30 and leftend == -1:
    #             leftend = row
    #         if mask_img[row, col] == 0 and mask_img[row-1, col] > 0 and row > 0:
    #             rightend = row
    #             # cv2.imwrite("mask_img.png", branding(mask_img, (i, j), 2))
    #             # print("leftend:({}, {}); rightedn:({}, {})\n".format(i, leftend, i, rightend))
    #             break
    #     max_wid = max(max_wid, rightend-leftend)
    
    # print("max width: {}".format(max_wid))
    return max_wid

# @author: Weixiong Lin
def max_width_2(mask):
    """
    Calculate width by light points
    """
    mask_img = mask
    ret, mask_img = cv2.threshold(mask_img, 30, 255, cv2.THRESH_BINARY)
    height, width = mask_img.shape

    # cv2.imwrite("shit.png", mask_img)
    max_wid = 0
    # count max width
    for i in range(height):
        # initialize leftend and rightend of mask area as -1
        row_width = 0
        for j in range(width-1):
            if mask_img[i, j] > 0:
                row_width += 1
        max_wid = max(max_wid, row_width)
    return max_wid

# @author: Weixiong Lin
def delete_seams(img, mask, paths):
    """Deleted the given seams in img

    Mark the pixels to be deleted in the matrix, copy the rest of them to new_img.

    Args:
        img: Numpy, given image to be processed.
        mask: Numpy, mask.
        paths: List of path of seams.

    Returns:
        new_img: New image with seams deleted.
        new_mask: New mask with deleted seams removed.

    Rasie:
        RuntimeError: Out of index.
    """
    print("img.shape", img.shape)
    print("mask.shape", mask.shape)
    height, width, _ = img.shape
    flag_matrix = np.zeros((height, width))
    for path in paths:
        for index in path:
            x, y = index
            flag_matrix[x, y] = -1
            img[x, y] = -1
    
    cv2.imwrite("seams.png", img)
    # print("nunmofpaths", len(paths))
    new_img = np.zeros((height, width-len(paths), 3), dtype=np.int16)
    new_mask = np.zeros((height, width-len(paths)))

    # Erase seams from img
    for i in range(height):
        col = 0
        for j in range(width):
            if flag_matrix[i, j] > -1:
                new_img[i, col] = img[i, j]
                col += 1
    
    # Erase seams from mask
    for i in range(height):
        col = 0
        for j in range(width):
            if flag_matrix[i, j] > -1:
                new_mask[i, col] = mask[i, j]
                col += 1
    return new_img, new_mask

# @author: Weixiong Lin
def add_seams(img, paths):
    height, width, _ = img.shape
    flag_matrix = np.zeros((height, width+len(paths)), dtype=np.int16)
    for path in paths:
        for index in path:
            x, y = index
            flag_matrix[x, y] = -1
    new_img = np.zeros((height, width+len(paths), 3), dtype=np.int16)
    # Erase seams from img
    for i in range(height):
        col = 0
        j = 0
        while col < width+len(paths):
            if flag_matrix[i, j] > -1:
                new_img[i, col] = img[i, j]
                col += 1
                j += 1
            else:
                new_img[i, col] = img[i, j]
                col += 1
                if j == 0 or j == width-1:
                    x, y = img[i, j], img[i, j]
                else:
                    x, y = img[i, j-1], img[i, j+1]
                new_img[i, col] = (x + y) // 2
                col += 1
                j += 1
    return new_img


# @author: Weixiong Lin
def add_seam(out_image, seam_idx):
    m, n = out_image.shape[: 2]
    output = np.zeros((m, n + 1, 3))
    for (row, col) in seam_idx:
        for ch in range(3):
            if col == 0:
                p = np.average(out_image[row, col: col + 2, ch])
                output[row, col, ch] = out_image[row, col, ch]
                output[row, col + 1, ch] = p
                output[row, col + 1:, ch] = out_image[row, col:, ch]
            else:
                p = np.average(out_image[row, col - 1: col + 1, ch])
                output[row, : col, ch] = out_image[row, : col, ch]
                output[row, col, ch] = p
                output[row, col + 1:, ch] = out_image[row, col:, ch]
    print("output.shape", output.shape)
    return output


mask = cv2.imread("../figures/duck_mask.jpg", 0)
ro_mask = cv2.imread("../figures/ro.jpg", 0)
print(max_width_2(mask))
print("=======================================")
print(max_width_2(ro_mask))
