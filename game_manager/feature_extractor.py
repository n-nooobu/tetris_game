import numpy as np

from board_manager import BOARD_DATA


def get_backBoard2d(BOARD_DATA):  #
    backBoard2d = np.array(BOARD_DATA.backBoard).reshape(-1, BOARD_DATA.width)
    backBoard2d = np.where(backBoard2d > 0, 1, 0)
    return backBoard2d


def get_backBoard1d(backBoard2d):
    backBoard1d = backBoard2d.reshape(-1)
    return list(backBoard1d)


def get_peaks_per_col(BOARD_DATA):
    backBoard2d = get_backBoard2d(BOARD_DATA)
    peaks = np.array([])
    for col in range(backBoard2d.shape[1]):
        if 1 in backBoard2d[:, col]:
            p = backBoard2d.shape[0] - np.argmax(backBoard2d[:, col], axis=0)
            peaks = np.append(peaks, p)
        else:
            peaks = np.append(peaks, 0)
    return peaks


def get_max_peak(BOARD_DATA):
    return np.max(get_peaks_per_col(BOARD_DATA))


def get_sum_peaks(BOARD_DATA):
    return np.sum(get_peaks_per_col(BOARD_DATA))


def get_nholes_per_col(BOARD_DATA):
    # Count from peaks to bottom
    backBoard2d = get_backBoard2d(BOARD_DATA)
    holes = []
    for col in range(BOARD_DATA.width):
        start = -get_peaks_per_col(BOARD_DATA)[col]
        # If there's no holes i.e. no blocks on that column
        if start == 0:
            holes.append(0)
        else:
            holes.append(np.count_nonzero(backBoard2d[int(start):, col] == 0))
    return holes


def get_sum_nholes(BOARD_DATA):
    return np.sum(get_nholes_per_col(BOARD_DATA))


def get_ncols_with_hole(BOARD_DATA):
    return np.count_nonzero(np.array(get_nholes_per_col(BOARD_DATA)) > 0)


def get_row_transition(BOARD_DATA):
    backBoard2d = get_backBoard2d(BOARD_DATA)
    max_peak = get_max_peak(BOARD_DATA)
    sum = 0
    # From highest peak to bottom
    for row in range(int(backBoard2d.shape[0] - max_peak), backBoard2d.shape[0]):
        for col in range(1, backBoard2d.shape[1]):
            if backBoard2d[row, col] != backBoard2d[row, col - 1]:
                sum += 1
    return sum


def get_col_transition(BOARD_DATA):
    backBoard2d = get_backBoard2d(BOARD_DATA)
    peaks = get_peaks_per_col(BOARD_DATA)
    sum = 0
    for col in range(backBoard2d.shape[1]):
        if peaks[col] <= 1:
            continue
        for row in range(int(backBoard2d.shape[0] - peaks[col]), backBoard2d.shape[0] - 1):
            if backBoard2d[row, col] != backBoard2d[row + 1, col]:
                sum += 1
    return sum


def get_bumpiness(BOARD_DATA):
    peaks = get_peaks_per_col(BOARD_DATA)
    s = 0
    for i in range(BOARD_DATA.width - 1):
        s += np.abs(peaks[i] - peaks[i + 1])
    return s


def get_num_pits(BOARD_DATA):
    backBoard2d = get_backBoard2d(BOARD_DATA)
    return np.count_nonzero(np.count_nonzero(backBoard2d, axis=0) == 0)


def get_wells(BOARD_DATA):
    peaks = get_peaks_per_col(BOARD_DATA)
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


def get_max_well(BOARD_DATA):
    return np.max(get_wells(BOARD_DATA))


def whether_can_put_I_in(BOARD_DATA, col10_peak):
    backBoard2d = get_backBoard2d(BOARD_DATA)
    cnt = 0
    for x in range(BOARD_DATA.width):
        for y in range(BOARD_DATA.height - (3 + int(col10_peak))):
            if backBoard2d[y, x]:
                cnt += 1
                break
    return cnt == BOARD_DATA.width


# Debug 1
"""BOARD_DATA.backBoard = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
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
print(get_peaks_per_col(BOARD_DATA))
print(get_max_peak(BOARD_DATA))
print(get_sum_peaks(BOARD_DATA))
print(get_nholes_per_col(BOARD_DATA))
print(get_sum_nholes(BOARD_DATA))
print(get_ncols_with_hole(BOARD_DATA))
print(get_row_transition(BOARD_DATA))
print(get_col_transition(BOARD_DATA))
print(get_bumpiness(BOARD_DATA))
print(get_num_pits(BOARD_DATA))
print(get_wells(BOARD_DATA))
print(get_max_well(BOARD_DATA))"""

# Debug 2
"""BOARD_DATA.backBoard = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
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
