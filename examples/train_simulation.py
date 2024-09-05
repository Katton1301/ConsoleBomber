from consolegame import playerdata as pd
from consolegame import neuralnetwork as nn
from consolegame import Game
import random


def simulate_game(game_count):
    game = 0
    while game < game_count:
        current_game = Game()
        current_game.add_resource_path("../resources/")
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
        current_game.start(False)

        while current_game.game_is_running():
            hero_action = current_game.action_to_symbol(random.randrange(5))
            current_game.run_day(hero_action, False)

        pd.collect_players_data("../resources/", "player.json")
        game += 1
        print(f'{game} game finished')


if __name__ == "__main__":
    simulate_game(500)
