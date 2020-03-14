import os
import re

if __name__ == "__main__":

    #path = input()
    path = "./wise_man_data/set/1"
    #path = "./wise_man"

    correct_file = re.compile(r'^ca[0-9]*.txt$')
    wise_file = re.compile(r'^wpa[0-9]*.txt$')

    P = 0
    N = 0

    TP = 0
    FP = 0

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
                        if file_indexes[index][1] >= 70:
                            TP += 1
                        valid_P += 1
                else:
                    N += 1
                    if index not in file_indexes.keys():
                        file_indexes[index] = [0, -1]
                    else:
                        file_indexes[index][0] = 0
                        if file_indexes[index][1] >= 70:
                            FP += 1
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
                            TP += 1
                            valid_P += 1
                        else:
                            FP += 1
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

    TPR = TP/valid_P
    FPR = FP/valid_N

    print(P, N, valid_P+valid_N, round(TPR, 3), round(FPR, 3))


    TP = 0
    FP = 0

    for key, answer in file_indexes.items():
        if answer[0] == 1 and answer[1] >= 70:
            TP += 1
        if answer[0] == 0 and answer[1] >= 70:
            FP += 1


    print(round(TPR, 3), round(FPR, 3))

