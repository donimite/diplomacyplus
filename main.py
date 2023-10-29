import cmd
from map import get_territories

class DiplomacyPlus(cmd.Cmd):
    intro = ("Welcome to Diplomacy+.\n"
             "Type help or ? to list commands.\n"
             "Available commands:\n"
             "  move <position> <unit> - Place a unit on the board.\n"
             "  show_board - Display the current state of the game board.\n"
             "  show_resources - Display the current state of your resources.\n"
             "  quit - Exit the game.\n")
    prompt = "(Diplomacy+) "

    def __init__(self):
        super().__init__()
        self.territories = get_territories()
        self.game_state = {
            'board': self.initialize_board(),
            'players': {},
            'current_player': None,
            'turn': 1,
            'season': 'spring',
        }
        self.setup_players()

    def setup_players(self):
        for i in range(3):
            player_name = input(f"Enter name for player {i+1}: ")
            self.game_state['players'][player_name] = {
                'capital': None,
                'land_of_importance': None,
                'resources': {'food': 10, 'energy': 1, 'material': 1, 'hearts': 1},
            }
            print(f"{player_name} has been added to the game!")

        self.game_state['current_player'] = list(self.game_state['players'].keys())[0]
        print(f"\n{self.game_state['current_player']} will start the game!")

    def initialize_board(self):
        board = {}

        # Defining specific tiles as unmovable, sea, or land
        for name, details in self.territories.items():
            board[name] = {
                'type': details['type'],
                'supply_center': details.get('supply_center', False),
                'coastal': details.get('coastal', False),
                'neighbors': details.get('neighbors', set()),
                'units': details.get('units', []),
                'owner': details.get('owner', None),
                'buildings': []  # if you want to keep track of buildings
            }
        return board

    def do_move(self, arg):
        """Move a unit. Usage: move <position> <unit>"""
        args = arg.split()
        if len(args) != 2:
            print("Invalid number of arguments. Usage: move <position> <unit>")
            return
        position, unit = args
        if position not in self.game_state['board']:
            print("Invalid position. Please choose a valid board position.")
            return
        if unit.lower() not in ['army', 'fleet']:
            print("Invalid unit type. Please choose either 'army' or 'fleet'.")
            return

        # Check if the unit is allowed to move to the specified position
        territory_type = self.game_state['board'][position]['type']
        if unit.lower() == 'army' and territory_type != 'land':
            print("Armies can only move to land territories.")
            return
        elif unit.lower() == 'fleet' and territory_type == 'land' and not self.game_state['board'][position]['coastal']:
            print("Fleets can only move to sea territories or coastal land territories.")
            return

        player = self.game_state['current_player']
        self.game_state['board'][position]['units'].append((player, unit.lower()))
        print(f"{player} moved {unit.lower()} to {position}")

        # Change to the next player's turn
        players = list(self.game_state['players'].keys())
        current_index = players.index(self.game_state['current_player'])
        next_index = (current_index + 1) % len(players)
        self.game_state['current_player'] = players[next_index]

    def do_show_board(self, arg):
        """Show the game board."""
        for position, info in self.game_state['board'].items():
            color = "\033[0m"  # Default to white
            if info['type'] == 'land':
                color = "\033[93m"  # Yellow
            elif info['type'] == 'sea':
                color = "\033[94m"  # Blue
            elif info['type'] == 'unmovable':
                color = "\033[90m"  # Grey
            print(f"{color}{position}: {info}\033[0m")  # Reset color after printing

    def do_show_resources(self, arg):
        """Show the current player's resources."""
        player = self.game_state['current_player']
        resources = self.game_state['players'][player]['resources']
        print(f"{player}'s resources: {resources}")

    def do_quit(self, arg):
        """Quit the game."""
        print("Thanks for playing!")
        return True

if __name__ == '__main__':
    DiplomacyPlus().cmdloop()
