import torch.cuda

from consolegame import playerdata as pd
from consolegame import neuralnetwork as nn
from consolegame import Game
import msvcrt

if __name__ == "__main__":

    createGame = True
    while createGame:
        new_game = Game()
        new_game.add_enemy_brain("../resources/")
        new_game.create_player("Hero", 0, 0)
        new_game.create_player("Enemy", 9, 9)
        new_game.start()

        while new_game.game_is_running():
            hero_action = msvcrt.getch().decode("utf-8")
            new_game.run_day(hero_action)

        new_game.print_game_result()

        print("Restart game - 0\nTrain and restart - 1\nExit - 2")
        restart = msvcrt.getch().decode("utf-8")
        if restart == "0":
            pd.collect_players_data("../resources/", "player.json", False)
        elif restart == "1":
            pd.collect_players_data("../resources/", "player.json", False)
            net = nn.GameNet("../resources/inputTrain.json")
            net.trainBrain()
        else:
            createGame = False
