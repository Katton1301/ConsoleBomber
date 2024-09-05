from consolegame import constants as const
from consolegame import playerdata as pd
from consolegame import neuralnetwork as nn
from consolegame import Game
import random
import msvcrt


def simulate_game(game_count):
    game = 0
    while game < game_count:
        current_game = Game(const.WIDTH, const.HEIGHT)
        current_game.create_player("Hero", random.randrange(10), random.randrange(10))
        free_places = current_game.get_free_places()
        [x, y] = random.choice(free_places)
        current_game.create_player("Enemy", x, y)
        free_places = current_game.get_free_places()
        [x, y] = random.choice(free_places)
        current_game.create_player("Enemy", x, y)
        free_places = current_game.get_free_places()
        [x, y] = random.choice(free_places)
        current_game.create_player("Enemy", x, y)
        current_game.hero.hit_points = 20
        while current_game.game_state != "End":
            current_game.day_init()
            if current_game.hero:
                current_game.save_hero_action(current_game.action_to_symbol(random.randrange(5)))
            current_game.calc_enemy_action()
            current_game.make_players_action()
            current_game.day_end()
        pd.collect_players_data("../resources/player.json")
        game += 1
        print(f'{game} game finished')


if __name__ == "__main__":
    # simulate_game(500)
    # exit()

    createGame = True
    while createGame:
        new_game = Game(const.WIDTH, const.HEIGHT)
        new_game.create_player("Hero", 0, 0)
        new_game.create_player("Enemy", 9, 9)
        new_game.create_player("Enemy", 0, 9)
        new_game.create_player("Enemy", 9, 0)
        new_game.draw()
        while new_game.game_state != "End":
            new_game.day_init()
            if new_game.hero:
                print("Hero action: ", end="")
                hero_action = msvcrt.getch().decode("utf-8")
                new_game.save_hero_action(hero_action)
            new_game.calc_enemy_action()
            new_game.end_field.day_end()
            new_game.make_players_action()
            new_game.day_end()
            new_game.draw()
        print(f'{new_game.winSide} win')
        print("Restart game - 0\nTrain and restart - 1\nExit - 2")
        restart = msvcrt.getch().decode("utf-8")
        if restart == "0":
            pd.collect_players_data("../resources/player.json", False)
        elif restart == "1":
            pd.collect_players_data("../resources/player.json", False)
            net = nn.GameNet("../resources/inputTrain.json")
            net.trainBrain()
        else:
            createGame = False
