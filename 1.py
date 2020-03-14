import os
import re

if __name__ == "__main__":

    #path = input()
    #path = "./wise_man_data/set/3"
    #path = "./wise_man"

    correct_file = re.compile(r'^ca[0-9]*.txt$')
    wise_file = re.compile(r'^wpa[0-9]*.txt$')

    P = 0
    N = 0

    valid_P = 0
    valid_N = 0

    file_indexes = {}

    for dirpath, dirnames, files in os.walk(path):
        for file in files:
            if correct_file.search(file):
                fullpath = os.path.join(dirpath, file)
                index = file[2:-4]
                f = open(fullpath, "r")
                if f.readline() == "Yes":
                    P += 1
                    if index not in file_indexes.keys():
                        file_indexes[index] = [1, -1]
                    else:
                        file_indexes[index][0] = 1
                        valid_P += 1
                else:
                    N += 1
                    if index not in file_indexes.keys():
                        file_indexes[index] = [0, -1]
                    else:
                        file_indexes[index][0] = 0
                        valid_N += 1
                f.close()
            elif wise_file.search(file):
                fullpath = os.path.join(dirpath, file)
                index = file[3:-4]
                f = open(fullpath, "r")
                threshold = int(f.readline()[:-1])
                if threshold >= 70:
                    if index not in file_indexes.keys():
                        file_indexes[index] = [-1, threshold]
                    else:
                        file_indexes[index][1] = threshold
                        if file_indexes[index][0] == 1:
                            valid_P += 1
                        else:
                            valid_N += 1

                else:
                    if index not in file_indexes.keys():
                        file_indexes[index] = [-1, threshold]
                    else:
                        file_indexes[index][1] = threshold
                        if file_indexes[index][0] == 1:
                            valid_P += 1
                        else:
                            valid_N += 1

                f.close()

    TP = 0
    FP = 0

    for key, answer in file_indexes.items():
        if answer[0] == 1 and answer[1] >= 70:
            TP += 1
        if answer[0] == 0 and answer[1] >= 70:
            FP += 1

    TPR = TP/valid_P
    FPR = FP/valid_N

    min = 1
    TPR_min = 0
    FPR_min = 0
    #optimizuj ne mora sve thresholdove da gleda
    for threshold in range(0, 101):
        TP = 0
        FP = 0
        for key, answer in file_indexes.items():
            if answer[0] == 1 and answer[1] >= threshold:
                TP += 1
            if answer[0] == 0 and answer[1] >= threshold:
                FP += 1
        TPR_try = TP/valid_P
        FPR_try = FP/valid_N
        print(round(1-TPR_try, 3), round(FPR_try, 3), abs(round(1 - TPR_try, 3) - round(FPR_try, 3)))
        tmp = abs(round(1 - TPR_try, 3) - round(FPR_try, 3))
        if tmp < min:
            min = tmp
            TPR_min = TPR_try
            FPR_min = FPR_try
        elif tmp > min:
            break


    print(f'{P},{N},{valid_P+valid_N},{round(TPR, 3)},{round(FPR, 3)},{round(FPR_min, 3)}')
