import json


def save_unique_data():
    main_file = "player.json"
    # noinspection PyBroadException
    try:
        with open(main_file, "r") as json_file:
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

    with open("player_check.json", 'w') as json_file:
        json.dump(main_data, json_file)


def collect_players_data():
    main_file = "player.json"
    # noinspection PyBroadException
    try:
        with open(main_file, "r") as json_file:
            main_data = json.load(json_file)
    except Exception:
        return
    for i in range(10):
        # noinspection PyBroadException
        try:
            with open("player_" + str(i) + ".json", "r") as json_file:
                data = json.load(json_file)
        except Exception:
            break
        if data:
            main_data[0] += data[0]
            main_data[1] += data[1]

    with open(main_file, 'w') as json_file:
        json.dump(main_data, json_file)


if __name__ == "__main__":
    save_unique_data()
