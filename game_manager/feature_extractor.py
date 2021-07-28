import numpy as np

from board_manager import BOARD_DATA


def get_backBoard2d(backboard, width):  #
    backBoard2d = np.array(backboard).reshape(-1, width)
    backBoard2d = np.where(backBoard2d > 0, 1, 0)
    return backBoard2d


def get_backBoard1d(backBoard2d):
    backBoard1d = backBoard2d.reshape(-1)
    return list(backBoard1d)


"""def get_peaks_per_col(BOARD_DATA):
    backBoard2d = get_backBoard2d(BOARD_DATA)
    peaks = np.array([])
    for col in range(backBoard2d.shape[1]):
        if 1 in backBoard2d[:, col]:
            p = backBoard2d.shape[0] - np.argmax(backBoard2d[:, col], axis=0)
            peaks = np.append(peaks, p)
        else:
            peaks = np.append(peaks, 0)
    return peaks"""


def get_peaks_per_col(backboard, width):
    backBoard2d = get_backBoard2d(backboard, width)
    peaks = np.zeros(backBoard2d.shape[1], dtype=int)
    for col in range(backBoard2d.shape[1]):
        for row in range(backBoard2d.shape[0]):
            if backBoard2d[row, col]:
                peaks[col] = backBoard2d.shape[0] - row
                break
    return peaks


def get_max_peak(backboard, width):
    return np.max(get_peaks_per_col(backboard, width))


def get_sum_peaks(backboard, width):
    return np.sum(get_peaks_per_col(backboard, width))


def get_nholes_per_col(backboard, width):
    # Count from peaks to bottom
    backBoard2d = get_backBoard2d(backboard, width)
    peaks = get_peaks_per_col(backboard, width)
    holes = []
    for col in range(width):
        start = -peaks[col]
        # If there's no holes i.e. no blocks on that column
        if start == 0:
            holes.append(0)
        else:
            holes.append(np.count_nonzero(backBoard2d[int(start):, col] == 0))
    return holes


def get_sum_nholes(backboard, width):
    return np.sum(get_nholes_per_col(backboard, width))


def get_ncols_with_hole(backboard, width):
    return np.count_nonzero(np.array(get_nholes_per_col(backboard, width)) > 0)


def get_row_transition(backboard, width):
    backBoard2d = get_backBoard2d(backboard, width)
    max_peak = get_max_peak(backboard, width)
    sum = 0
    # From highest peak to bottom
    for row in range(int(backBoard2d.shape[0] - max_peak), backBoard2d.shape[0]):
        for col in range(1, backBoard2d.shape[1]):
            if backBoard2d[row, col] != backBoard2d[row, col - 1]:
                sum += 1
    return sum


def get_col_transition(backboard, width):
    backBoard2d = get_backBoard2d(backboard, width)
    peaks = get_peaks_per_col(backboard, width)
    sum = 0
    for col in range(backBoard2d.shape[1]):
        if peaks[col] <= 1:
            continue
        for row in range(int(backBoard2d.shape[0] - peaks[col]), backBoard2d.shape[0] - 1):
            if backBoard2d[row, col] != backBoard2d[row + 1, col]:
                sum += 1
    return sum


def get_bumpiness(backboard, width):
    peaks = get_peaks_per_col(backboard, width)
    s = 0
    for i in range(width - 1):
        s += np.abs(peaks[i] - peaks[i + 1])
    return s


def get_num_pits(backboard, width):
    backBoard2d = get_backBoard2d(backboard, width)
    return np.count_nonzero(np.count_nonzero(backBoard2d, axis=0) == 0)


def get_wells(backboard, width):
    peaks = get_peaks_per_col(backboard, width)
    wells = []
    for i in range(len(peaks)):
        if i == 0:
            w = peaks[1] - peaks[0]
            w = w if w > 0 else 0
            wells.append(w)
        elif i == len(peaks) - 1:
            w = peaks[-2] - peaks[-1]
            w = w if w > 0 else 0
            wells.append(w)
        else:
            w1 = peaks[i - 1] - peaks[i]
            w2 = peaks[i + 1] - peaks[i]
            w1 = w1 if w1 > 0 else 0
            w2 = w2 if w2 > 0 else 0
            w = w1 if w1 >= w2 else w2
            wells.append(w)
    return wells


def get_max_well(backboard, width):
    return np.max(get_wells(backboard, width))


def get_wells2(backboard, width, height):
    peaks = get_peaks_per_col(backboard, width)
    wells = []
    for col in range(width):
        if col == 0:
            pre_peak = height
        else:
            pre_peak = peaks[col - 1]
        now_peak = peaks[col]
        if col == width - 1:
            nxt_peak = height
        else:
            nxt_peak = peaks[col + 1]
        w = min(max(pre_peak - now_peak, 0), max(nxt_peak - now_peak, 0))
        wells.append(w)
    return wells


def get_max_well2(backboard, width, height):
    return np.max(get_wells2(backboard, width, height))


def whether_can_put_I_in(backboard, width, height, col10_peak):
    backBoard2d = get_backBoard2d(backboard, width)
    cnt = 0
    for x in range(width):
        for y in range(height - (3 + int(col10_peak))):
            if backBoard2d[y, x]:
                cnt += 1
                break
    return cnt == width


# Debug 1
"""backboard = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
             0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
             0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
             0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
             0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
             0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
             0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
             0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
             0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
             0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
             0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
             1, 0, 0, 0, 0, 0, 0, 0, 0, 0,
             1, 0, 0, 0, 0, 0, 0, 0, 0, 0,
             1, 0, 0, 0, 0, 0, 0, 0, 0, 0,
             1, 0, 0, 0, 0, 0, 0, 0, 0, 0,
             1, 1, 0, 1, 0, 0, 0, 0, 0, 0,
             1, 1, 0, 1, 0, 0, 0, 0, 0, 0,
             1, 1, 0, 1, 1, 0, 1, 0, 0, 0,
             1, 1, 1, 1, 1, 0, 1, 0, 0, 0,
             1, 0, 1, 1, 1, 1, 1, 0, 0, 0,
             1, 1, 1, 1, 1, 1, 1, 0, 0, 0,
             1, 0, 1, 0, 1, 0, 1, 0, 0, 0]
width = 10
height = 22
print(get_peaks_per_col(backboard, width))
print(get_max_peak(backboard, width))
print(get_sum_peaks(backboard, width))
print(get_nholes_per_col(backboard, width))
print(get_sum_nholes(backboard, width))
print(get_ncols_with_hole(backboard, width))
print(get_row_transition(backboard, width))
print(get_col_transition(backboard, width))
print(get_bumpiness(backboard, width))
print(get_num_pits(backboard, width))
print(get_wells(backboard, width))
print(get_max_well(backboard, width))"""

# Debug 2
"""-BOARD_DATA.backBoard = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                        0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                        0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                        0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                        0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                        0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                        0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                        0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                        0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                        0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                        0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                        1, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                        1, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                        1, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                        1, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                        1, 1, 0, 1, 0, 0, 0, 0, 0, 0,
                        1, 1, 0, 1, 0, 0, 0, 0, 1, 0,
                        1, 1, 0, 1, 1, 0, 1, 1, 0, 0,
                        1, 1, 1, 1, 1, 1, 1, 0, 0, 1,
                        1, 0, 1, 1, 1, 1, 1, 0, 0, 0,
                        1, 1, 1, 1, 1, 1, 1, 0, 0, 0,
                        1, 0, 1, 0, 1, 0, 1, 0, 0, 0]
print(whether_can_put_I_in(BOARD_DATA, 0))"""
