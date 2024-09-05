import json


def save_unique_data(path, main_file):
    # noinspection PyBroadException
    try:
        with open(path + "/" + main_file, "r") as json_file:
            main_data = json.load(json_file)
    except Exception:
        return

    unique_data = [[], []]

    def is_unique_params(params):
        for unique_params in unique_data[0]:
            is_unique = False
            for i_num in range(0, len(params) - 1):
                if params[i_num] != unique_params[i_num]:
                    is_unique = True
                    break
            if not is_unique:
                return False
        return True

    for i in range(len(main_data[0])):
        if i % 100 == 0:
            print(i)
        if is_unique_params(main_data[0][i]):
            unique_data[0] += [main_data[0][i]]
            unique_data[1] += [main_data[1][i]]

    with open(path + "/player_check.json", 'w') as json_file:
        json.dump(main_data, json_file)


def collect_players_data(path, main_file, normalize=True):
    # noinspection PyBroadException
    try:
        with open(path + main_file, "r") as json_file:
            main_data = json.load(json_file)
    except Exception:
        return

    for i in range(10):
        data = None
        # noinspection PyBroadException
        try:
            with open(path + "player_" + str(i) + ".json", "r") as json_file:
                data = json.load(json_file)
                if normalize:
                    normalize_data = [[], []]
                    for j in range(len(data[1])):
                        if data[1][j] == 3:
                            normalize_data[0] += [data[0][j]]
                            normalize_data[1] += [data[1][j]]
                    k = len(normalize_data[0])
                    if k == 0:
                        break
                    for j in range(len(data[1])):
                        if data[1][j] == 0:
                            normalize_data[0] += [data[0][j]]
                            normalize_data[1] += [data[1][j]]
                        if k * 2 <= len(normalize_data[0]):
                            break
                    for j in range(len(data[1])):
                        if data[1][j] == 1:
                            normalize_data[0] += [data[0][j]]
                            normalize_data[1] += [data[1][j]]
                        if k * 3 <= len(normalize_data[0]):
                            break
                    for j in range(len(data[1])):
                        if data[1][j] == 2:
                            normalize_data[0] += [data[0][j]]
                            normalize_data[1] += [data[1][j]]
                        if k * 4 <= len(normalize_data[0]):
                            break
                    data = normalize_data
        except Exception:
            pass
        if data:
            main_data[0] += data[0]
            main_data[1] += data[1]

    with open(path + main_file, 'w') as json_file:
        json.dump(main_data, json_file)
