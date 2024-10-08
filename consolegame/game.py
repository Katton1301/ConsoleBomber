import random
import json
from . import neuralnetwork as nn

# constants
_ATTACK_LOADING = 5
_BONUS_LOADING = 5
_DEFAULT_HP = 10
_HEIGHT = 10
_WIDTH = 10
_DAYS_TO_START_END = 20


def print_rules():
    print(
        "Game rules",
        "Task: Survive longer than enemies",
        "Control:",
        "\'W\' - move up",
        "\'S\' - move down",
        "\'A\' - move left",
        "\'D\' - move right",
        "\'Space\' - Attack",
        "Attack damage is dealt around th player",
        "Bonuses:",
        "\'+\' - heal one hit point",
        "\'*\' - increase attack range",
        sep="\n"
    )


class Game:
    def __init__(self, _width=_WIDTH, _height=_HEIGHT):

        self.width = _width
        self.height = _height
        self.hero = None
        self.players_list = []
        self.bonus_list = []
        self.game_day = 0
        self.game_state = "Start"
        self.winSide = "Draw"
        self.bonus_days_left = _BONUS_LOADING
        self.players_dead = 0

        self.end_field = EndField(_DAYS_TO_START_END, _width, _height)
        self.net = None
        self.modelLoaded = False
        self.resources_path = None

    def add_resource_path(self, _resources_path):
        self.resources_path = _resources_path
    def add_enemy_brain(self, _resources_path):
        self.resources_path = _resources_path
        self.net = nn.GameNet(self.resources_path + "inputNet.json")
        self.modelLoaded = self.net.loadModel()

    def check_to_bonus(self):
        for player in self.players_list:
            for bonus in self.bonus_list:
                if bonus.x == player.x and bonus.y == player.y:
                    if bonus.bonus_type == 0:
                        player.hit_points += 1
                    else:
                        player.damageRate += 1
                    self.bonus_list.remove(bonus)
                    player.bonus_activate = True
                    del bonus

    def check_to_damage(self):
        damage_coordinates = set()
        for player in self.players_list:
            if player.attack:
                if player.damageRate > 0:
                    if player.x + 1 < self.width:
                        damage_coordinates.add((player.x + 1) * self.width + player.y)
                    if player.x - 1 >= 0:
                        damage_coordinates.add((player.x - 1) * self.width + player.y)
                    if player.y + 1 < self.height:
                        damage_coordinates.add(player.x * self.width + player.y + 1)
                    if player.y - 1 >= 0:
                        damage_coordinates.add(player.x * self.width + player.y - 1)

                    if player.damageRate > 1:
                        if player.x + 1 < self.width and player.y + 1 < self.height:
                            damage_coordinates.add((player.x + 1) * self.width + player.y + 1)
                        if player.x - 1 >= 0 and player.y - 1 >= 0:
                            damage_coordinates.add((player.x - 1) * self.width + player.y - 1)
                        if player.x - 1 >= 0 and player.y + 1 < self.height:
                            damage_coordinates.add((player.x - 1) * self.width + player.y + 1)
                        if player.x + 1 < self.width and player.y - 1 >= 0:
                            damage_coordinates.add((player.x + 1) * self.width + player.y - 1)

                        if player.damageRate > 2:
                            if player.x + 2 < self.width:
                                damage_coordinates.add((player.x + 2) * self.width + player.y)
                            if player.x - 2 >= 0:
                                damage_coordinates.add((player.x - 2) * self.width + player.y)
                            if player.y + 2 < self.height:
                                damage_coordinates.add(player.x * self.width + player.y + 2)
                            if player.y - 2 >= 0:
                                damage_coordinates.add(player.x * self.width + player.y - 2)

        for player in self.players_list:
            if (player.x * self.width + player.y) in damage_coordinates and not player.damage:
                player.get_damage()
            else:
                for [x, y] in self.end_field.end_list:
                    if player.x == x and player.y == y:
                        player.get_damage()

    def check_to_making_damage(self, player):
        damage_points = 0
        for enemy in self.players_list:
            if enemy.side != player.side and enemy.damage:
                if player.damageRate == 1:
                    if abs(enemy.y - player.y) + abs(enemy.x - player.x) <= 1:
                        damage_points += 2 if enemy.hit_points == 0 else 1
                elif player.damageRate == 2:
                    if abs(enemy.y - player.y) <= 1 and abs(enemy.x - player.x) <= 1:
                        damage_points += 2 if enemy.hit_points == 0 else 1
                elif player.damageRate > 2:
                    if abs(enemy.y - player.y) + abs(enemy.x - player.x) <= 2:
                        damage_points += 2 if enemy.hit_points == 0 else 1
        return damage_points

    def get_param_near_enemy(self, player):
        min_dist = self.width + self.height
        near_enemy = None
        for enemy in self.players_list:
            if player.side != enemy.side:
                dist = abs(player.x - enemy.x) + abs(player.y - enemy.y)
                if dist < min_dist:
                    near_enemy = enemy
                    min_dist = dist
        if near_enemy:
            return [player.x - near_enemy.x, player.y - near_enemy.y, near_enemy.damageRate, near_enemy.attack_ready]
        else:
            return [self.width, self.height, 0, _ATTACK_LOADING]

    def get_param_near_bonuses(self, player):
        min_dist_heal_bonus = self.width + self.height
        min_dist_damage_bonus = self.width + self.height
        near_heal_bonus = None
        near_damage_bonus = None
        for bonus in self.bonus_list:
            dist = abs(player.x - bonus.x) + abs(player.y - bonus.y)
            if bonus.bonus_type == 0:
                if dist < min_dist_heal_bonus:
                    min_dist_heal_bonus = dist
                    near_heal_bonus = bonus
            else:
                if dist < min_dist_damage_bonus:
                    min_dist_damage_bonus = dist
                    near_damage_bonus = bonus

        if near_heal_bonus:
            bonus_heal_dist_x = player.x - near_heal_bonus.x
            bonus_heal_dist_y = player.y - near_heal_bonus.y
        else:
            bonus_heal_dist_x = self.width
            bonus_heal_dist_y = self.height

        if near_damage_bonus:
            bonus_damage_dist_x = player.x - near_damage_bonus.x
            bonus_damage_dist_y = player.y - near_damage_bonus.y
        else:
            bonus_damage_dist_x = self.width
            bonus_damage_dist_y = self.height

        return [bonus_heal_dist_x, bonus_heal_dist_y,
                bonus_damage_dist_x, bonus_damage_dist_y]

    def make_players_action(self):
        players_coord = {}
        players_cancel_action = []
        for i in range(len(self.players_list)):
            player = self.players_list[i]
            x = player.x
            y = player.y
            if player.action == "w":
                if player.y < self.height - 1:
                    y += 1
            elif player.action == "s":
                if player.y > 0:
                    y -= 1
            elif player.action == "d":
                if player.x < self.width - 1:
                    x += 1
            elif player.action == "a":
                if player.x > 0:
                    x -= 1
            x_y = x * self.width + y
            if x_y in players_coord:
                if len(players_coord[x_y]) == 1:
                    players_cancel_action.append(players_coord[x_y][0])
                players_coord[x_y].append(i)
                players_cancel_action.append(i)
            else:
                players_coord[x_y] = [i]

        for i in range(len(self.players_list)):
            player = self.players_list[i]
            if player.action == "w":
                if player.y < self.height - 1:
                    if i not in players_cancel_action:
                        player.y += 1
                else:
                    player.get_damage()
            elif player.action == "s":
                if player.y > 0:
                    if i not in players_cancel_action:
                        player.y -= 1
                else:
                    player.get_damage()
            elif player.action == "d":
                if player.x < self.width - 1:
                    if i not in players_cancel_action:
                        player.x += 1
                else:
                    player.get_damage()
            elif player.action == "a":
                if player.x > 0:
                    if i not in players_cancel_action:
                        player.x -= 1
                else:
                    player.get_damage()
            elif player.action == " ":
                if player.attack_ready == 0:
                    player.attack = True
                else:
                    player.get_damage()
            else:
                print(f'Unknown action - {player.action}')
                player.get_damage()
        self.check_to_bonus()
        self.check_to_damage()

    def create_player(self, side, _x=0, _y=0):
        player = Player(side, _x, _y)
        if side == "Hero":
            if self.hero:
                print("Hero already created")
                return
            else:
                self.hero = player

        self.players_list.append(player)

    @staticmethod
    def action_to_symbol(action):
        if action == 4:
            return " "
        elif action % 2 == 0:
            if action == 0:
                return "w"
            else:
                return "s"
        else:
            if action == 1:
                return "d"
            else:
                return "a"

    @staticmethod
    def symbol_to_action(symbol):
        if symbol == "w":
            return 0
        elif symbol == "d":
            return 1
        elif symbol == "s":
            return 2
        elif symbol == "a":
            return 3
        elif symbol == " ":
            return 4
        return -1

    @staticmethod
    def change_params(input_params, action):
        if action == 4:
            input_params[6] += _ATTACK_LOADING
        elif action % 2 == 0:
            if action == 0:
                input_params[2] += 1
                input_params[3] -= 1
            else:
                input_params[2] -= 1
                input_params[3] += 1
        else:
            if action == 1:
                input_params[0] += 1
                input_params[1] -= 1
            else:
                input_params[0] -= 1
                input_params[1] += 1
        return input_params

    def predict_action(self, input_params):
        best_action = -1
        max_points = 0
        best_param = input_params
        for action in range(5):
            changing_params = self.change_params(input_params, action)
            predict_points = self.net.predict_action(changing_params)
            if predict_points > max_points:
                max_points = predict_points
                best_action = action
                best_param = changing_params
        return [self.action_to_symbol(best_action), best_param]

    def random_action(self, input_params):
        action = random.randrange(5)
        changing_params = self.change_params(input_params, action)
        return [self.action_to_symbol(action), changing_params]

    def collect_params(self, player):
        [
            enemy_dist_x, enemy_dist_y,
            enemy_attack_damage, enemy_attack_ready
        ] = self.get_param_near_enemy(player)

        [
            bonus_heal_dist_x, bonus_heal_dist_y,
            bonus_damage_dist_x, bonus_damage_dist_y
        ] = self.get_param_near_bonuses(player)

        return [
            player.x,
            self.width - player.x,
            player.y,
            self.height - player.y,
            player.hit_points,
            player.damageRate,
            player.attack_ready,
            enemy_dist_x,
            enemy_dist_y,
            enemy_attack_damage,
            enemy_attack_ready,
            self.bonus_days_left,
            bonus_heal_dist_x,
            bonus_heal_dist_y,
            bonus_damage_dist_x,
            bonus_damage_dist_y
        ]

    def save_hero_action(self, action):
        int_action = self.symbol_to_action(action)
        input_params = self.collect_params(self.hero)
        changing_params = self.change_params(input_params, int_action)
        self.hero.action = action
        self.hero.history.add_day_history_params(*changing_params)

    def calc_enemy_action(self):
        for player in self.players_list:
            if player.side != "Hero":
                input_params = self.collect_params(player)
                if self.modelLoaded:
                    [player.action, input_params] = self.predict_action(input_params)
                else:
                    [player.action, input_params] = self.random_action(input_params)
                player.history.add_day_history_params(*input_params)

    def get_free_places(self):
        free_places = []
        for i in range(self.height):
            for j in range(self.width):
                for player in self.players_list:
                    if player.x == j and player.y == i:
                        break
                for bonus in self.bonus_list:
                    if bonus.x == j and bonus.y == i:
                        break
                for [x, y] in self.end_field.end_list:
                    if x == j and y == i:
                        break
                free_places.append([j, i])
        return free_places

    def day_init(self):
        self.game_day += 1
        for player in self.players_list:
            player.damage = False
            player.bonus_activate = False

    def day_end(self):
        deleted_players = []
        for player in self.players_list:
            points = 1
            if player.damage:
                points = 0
            if player.bonus_activate:
                points = 2
            if self.check_to_making_damage(player) > 0:
                points = 3

            if player.attack:
                player.attack = False
                player.attack_ready = _ATTACK_LOADING
            elif player.attack_ready > 0:
                player.attack_ready -= 1
            if player.hit_points == 0:
                player.history.remember_history(0)
                self.players_dead += 1
                if self.resources_path:
                    file_saved = player.history.save_in_json(self.resources_path + "player_" + str(self.players_dead) +
                                                             ".json")
                    if not file_saved:
                        print(player.side, " history don't saved")
                if player.side == "Hero":
                    self.hero = None
                deleted_players.append(player)
            else:
                player.history.remember_history(points)

        for del_player in deleted_players:
            self.players_list.remove(del_player)
            del del_player

        deleted_bonuses = []
        for bonus in self.bonus_list:
            for [x, y] in self.end_field.end_list:
                if bonus.x == x and bonus.y == y:
                    deleted_bonuses.append(bonus)
        for del_bonus in deleted_bonuses:
            self.bonus_list.remove(del_bonus)
            del del_bonus

        self.bonus_days_left -= 1
        if self.bonus_days_left == 0:
            free_places = self.get_free_places()
            if len(free_places) > 0:
                self.bonus_days_left = _BONUS_LOADING
                [x, y] = random.choice(free_places)
                self.bonus_list.append(Bonus(1 if random.randrange(5) == 0 else 0, x, y))

        if self.hero is None:
            self.game_state = "End"
            self.winSide = "Enemy"
        elif len(self.players_list) == 1:
            self.game_state = "End"
            self.winSide = "Hero"

    def draw(self):
        print(f'\nGame day: {self.game_day}')
        if self.bonus_days_left > 0:
            print(f'Bonus days left: {self.bonus_days_left}')
        print("       ", end="")
        for player in self.players_list:
            print("{:<6}".format(player.side), end=" ")
        print()
        print("HP:    ", end="")
        for player in self.players_list:
            print("{:<6}".format(player.hit_points), end=" ")
        print()
        print("Attack:", end="")
        for player in self.players_list:
            print("{:<6}".format(
                "Ready" if player.attack_ready == 0 else
                "Attack" if player.attack_ready == _ATTACK_LOADING else player.attack_ready),
                end=" ")
        print("\n ", end="")
        print(self.width * "-")
        for i in range(self.height - 1, -1, -1):
            print("|", end="")
            for j in range(self.width):
                char = " "
                for bonus in self.bonus_list:
                    if i == bonus.y and j == bonus.x:
                        if bonus.bonus_type == 0:
                            char = "+"
                        else:
                            char = "*"

                for [x, y] in self.end_field.end_list:
                    if y == i and x == j:
                        char = "x"

                for player in self.players_list:
                    if i == player.y and j == player.x:
                        if player.side == "Hero":
                            if player.damage:
                                char = "h"
                            else:
                                char = "H"
                        else:
                            if player.damage:
                                char = "e"
                            else:
                                char = "E"
                        break
                    elif player.attack_ready == _ATTACK_LOADING:
                        if player.damageRate == 1:
                            if abs(i - player.y) + abs(j - player.x) <= 1:
                                char = "#"
                        elif player.damageRate == 2:
                            if abs(i - player.y) <= 1 and abs(j - player.x) <= 1:
                                char = "#"
                        elif player.damageRate > 2:
                            if abs(i - player.y) + abs(j - player.x) <= 2:
                                char = "#"

                print(char, end="")
            print("|")
        print(" ", end="")
        print(self.width * "-")

    def start(self, is_print=True):

        if is_print:
            print_rules()
            self.draw()
        if self.hero:
            self.day_init()
            if is_print:
                print("Choose action: ", end="")

    def run_day(self, hero_action, is_print=True):
        self.save_hero_action(hero_action)
        self.calc_enemy_action()
        self.end_field.day_end()
        self.make_players_action()
        self.day_end()
        if is_print:
            self.draw()
        if self.hero and self.game_is_running:
            self.day_init()
            if is_print:
                print("Choose action: ", end="")

    def print_game_result(self):
        print(f'{self.winSide} win')

    def game_is_running(self):
        return self.game_state != "End"


class Player:
    def __init__(self, side, _x=0, _y=0):
        self.side = side
        self.x = _x
        self.y = _y
        self.hit_points = _DEFAULT_HP
        self.bonus_activate = False

        self.attack_ready = 0
        self.attack = False

        self.damage = False
        self.damageRate = 1

        self.action = ""
        self.history = History()

    def get_damage(self):
        if not self.damage:
            self.hit_points -= 1
            self.damage = True


class Bonus:
    def __init__(self, _bonus_type, _x=0, _y=0):
        # bonus type define
        # 0 heal
        # 1 damage upgrade
        self.x = _x
        self.y = _y
        self.bonus_type = _bonus_type


class History:
    def __init__(self):
        self.history_points = []
        self.history_params = []

    def add_day_history_params(
            self,
            left_dist,
            right_dist,
            top_dist,
            bottom_dist,
            hit_points,
            attack_damage,
            attack_ready,
            enemy_dist_x,
            enemy_dist_y,
            enemy_attack_damage,
            enemy_attack_ready,
            bonus_days_left,
            bonus_heal_dist_x,
            bonus_heal_dist_y,
            bonus_damage_dist_x,
            bonus_damage_dist_y
    ):
        self.history_params.append([
            left_dist,
            right_dist,
            top_dist,
            bottom_dist,
            hit_points,
            attack_damage,
            attack_ready,
            enemy_dist_x,
            enemy_dist_y,
            enemy_attack_damage,
            enemy_attack_ready,
            bonus_days_left,
            bonus_heal_dist_x,
            bonus_heal_dist_y,
            bonus_damage_dist_x,
            bonus_damage_dist_y
        ])

    def remember_history(self, points):
        self.history_points.append(points)

    def save_in_json(self, filename):
        with open(filename, 'w') as json_file:
            if len(self.history_params) != len(self.history_points):
                print("Error-", filename)
                return False
            json.dump([self.history_params, self.history_points], json_file)
        return True


class EndField:
    def __init__(self, days_to_end, width, height):
        self.daysToEnd = days_to_end
        self.fieldSize = width * height
        self.bottom = 0
        self.top = height - 1
        self.left = 0
        self.right = width - 1
        self.direction = 0
        self.x = 0
        self.y = 0
        self.end_list = []

    def day_end(self):
        if len(self.end_list) < self.fieldSize:
            if self.daysToEnd > 0:
                self.daysToEnd -= 1
            else:
                self.end_list.append([self.x, self.y])
                if self.direction == 0:
                    self.x += 1
                    if self.x == self.right:
                        self.bottom += 1
                        self.direction = 1
                elif self.direction == 1:
                    self.y += 1
                    if self.y == self.top:
                        self.right -= 1
                        self.direction = 2
                elif self.direction == 2:
                    self.x -= 1
                    if self.x == self.left:
                        self.top -= 1
                        self.direction = 3
                else:
                    self.y -= 1
                    if self.y == self.bottom:
                        self.left += 1
                        self.direction = 0
