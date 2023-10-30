import cmd
import pygame
import sys
import random
from map import get_territories

class DiplomacyPlus(cmd.Cmd):
    intro = ("Welcome to Diplomacy+.\n"
         "Type help or ? to list commands.\n"
         "Available commands:\n"
         "  move <from_territory> <to_territory> - Move a unit from one territory to another.\n"
         "  show_board - Display the current state of the game board.\n"
         "  show_resources - Display the current state of your resources.\n"
         "  show - Display the territories you currently hold.\n"
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
      self.game_state['turn'] = 1
      self.game_state['phase'] = 'Diplomacy'
      self.setup_players()
  
      # Initialize Pygame
      pygame.init()
      self.screen = pygame.display.set_mode((800, 800))
      pygame.display.set_caption("Diplomacy+")

    def setup_players(self):
        land_territories = [t for t, info in self.territories.items() if info['type'] == 'land']

        for i in range(3):
            player_name = input(f"Enter name for player {i+1}: ")
            self.game_state['players'][player_name] = {
                'capital': None,
                'land_of_importance': None,
                'resources': {'food': 10, 'energy': 1, 'material': 1, 'hearts': 1},
            }

            # Ensure there are enough territories for the players
            if len(land_territories) < 3:
                print("Not enough land territories for all players!")
                return

            # Randomly select 3 land territories for the player
            player_territories = random.sample(land_territories, 3)

            for territory in player_territories:
                # Remove this territory from the list so it's not chosen again
                land_territories.remove(territory)

                # Check if the territory is coastal
                is_coastal = self.territories[territory]['coastal']

                # Decide unit type
                if is_coastal and random.choice([True, False]):
                    unit_type = 'fleet'
                else:
                    unit_type = 'army'

                # Assign the territory and unit to the player
                self.game_state['board'][territory]['owner'] = player_name
                self.game_state['board'][territory]['units'].append((player_name, unit_type))

                # Add resources for supply centers
                if self.territories[territory].get('supply_center', False):
                    self.game_state['players'][player_name]['resources']['hearts'] += 1

            print(f"{player_name} has been assigned territories: {player_territories}")
            print(f"{player_name} has been added to the game!")

        self.game_state['current_player'] = list(self.game_state['players'].keys())[0]
        print(f"\n{self.game_state['current_player']} will start the game!")


    def initialize_board(self):
        board = {}
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

    def next_phase(self):
        phases = ['Diplomacy', 'Order Writing', 'Order Resolution', 'Retreat and Disbanding', 'Gain and Losses']
        current_index = phases.index(self.game_state['phase'])
        next_index = (current_index + 1) % len(phases)
        self.game_state['phase'] = phases[next_index]

        if next_index == 0:
            self.game_state['turn'] += 1
            print(f"Turn {self.game_state['turn']}, {self.game_state['phase']} Phase")
        else:
            print(f"{self.game_state['phase']} Phase")

        if self.game_state['phase'] == 'Diplomacy':
            print("Players discuss and form alliances.")
        elif self.game_state['phase'] == 'Order Writing':
            print("Each player writes down their orders.")
        elif self.game_state['phase'] == 'Order Resolution':
            self.resolve_orders()
            print("Orders are resolved. Conflicts are resolved. Units are moved.")
        elif self.game_state['phase'] == 'Retreat and Disbanding':
            print("Units in retreat must move or disband. Players adjust their unit counts.")
        elif self.game_state['phase'] == 'Gain and Losses':
            print("Players gain or lose units based on the number of supply centers they control.")

            
    def do_next_phase(self, arg):
        """Transition to the next phase."""
        self.next_phase()

    def do_order(self, arg):
        """Write an order for a unit. Usage: order [unit] [action] [source] [destination]"""
        args = arg.split()
        if len(args) != 4:
            print("Invalid number of arguments. Usage: order [unit] [action] [source] [destination]")
            return

        unit, action, source, destination = args
        player = self.game_state['current_player']

        # Check if the unit is in the source territory
        if (player, unit) not in self.game_state['board'][source]['units']:
            print("You do not have that unit in the specified source territory.")
            return

        # Write the order
        order = {
            'player': player,
            'unit': unit,
            'action': action,
            'source': source,
            'destination': destination,
        }
        self.game_state['orders'].append(order)
        print(f"Order written: {player}'s {unit} in {source} will {action} to {destination}")

    def resolve_orders(self):
        # Dictionary to store the destination of each unit
        destinations = {}
        # Set to store territories with conflicts
        conflicts = set()

        # Resolve movements
        for order in self.game_state['orders']:
            if order['action'] == 'move':
                # Check if another unit is trying to move to the same destination
                if order['destination'] in destinations.values():
                    conflicts.add(order['destination'])
                destinations[order['source']] = order['destination']

        # Apply movements, skipping units that are involved in conflicts
        for source, destination in destinations.items():
            if destination not in conflicts:
                player, unit = self.game_state['board'][source]['units'].pop()
                self.game_state['board'][destination]['units'].append((player, unit))
                print(f"{player}'s {unit} moved from {source} to {destination}")
            else:
                print(f"Conflict in {destination}. Units involved did not move.")

        # Clear orders after resolution
        self.game_state['orders'] = []

    def do_show(self, arg):
        """Show the territories currently held by the player."""
        player = self.game_state['current_player']
        print(f"\n{player}'s territories:")
    
        owned_territories = {name: info for name, info in self.game_state['board'].items() if info['owner'] == player}
        if not owned_territories:
            print("You currently do not own any territories.")
            return
    
        for position, info in owned_territories.items():
            print(f"{position}: {info}")
        print()

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
        pygame.quit()
        return True

    def draw_board(self):
      self.screen.fill((255, 255, 255))  # White background
      for position, info in self.game_state['board'].items():
          x, y = self.get_territory_position(position)
  
          # Define colors
          border_color = (169, 169, 169)  # Light black (grey)
          land_color = (0, 128, 0)  # Green
          #water blue for sea color
          sea_color = (0, 0, 255)
         
  
          # Choose the appropriate color based on the territory type
          color = land_color if info['type'] == 'land' else sea_color
  
          # Draw territory square with a light black border
          pygame.draw.rect(self.screen, border_color, (x, y, 60, 60), 1)
          pygame.draw.rect(self.screen, color, (x+1, y+1, 58, 58))
  
          # Draw territory name
          font = pygame.font.Font(None, 24)
          text = font.render(position, True, (255, 255, 255))  # White text
          text_rect = text.get_rect(center=(x+30, y+30))
          self.screen.blit(text, text_rect)
        
    def get_territory_position(self, position):
        # Positions adjusted for 800x800 canvas size.
        positions = {
            'LON': (160, 320),
            'YOR': (160, 240),
            'WAL': (80, 320),
            'LVP': (80, 240),
            'CLY': (80, 160),
            'EDI': (160, 160),
            'BEL': (240, 320),
            'HOL': (320, 320),
            'DEN': (320, 240),
            'KIE': (320, 400),
            'BER': (400, 400),
            'MUN': (400, 480),
            'RUH': (240, 400),
            'BUR': (240, 480),
            'PIC': (160, 400),
            'BRE': (80, 400),
            'GAS': (80, 480),
            'PAR': (160, 480),
            'MAR': (160, 560),
            'PIE': (240, 560),
            'VEN': (320, 560),
            'TUS': (240, 640),
            'ROM': (320, 640),
            'NAP': (320, 720),
            'SWE': (400, 240),
            'NOR': (320, 160),
            'STP': (480, 160),
            'FIN': (480, 240),
            'NWY': (400, 160),
            'SKA': (400, 320),
            'BAL': (480, 320),
            'Pru': (480, 400),
            'SIL': (480, 480),
            'BOH': (400, 560),
            'VIE': (480, 560),
            'GAL': (560, 480),
            'WAR': (560, 400),
            'UKR': (640, 400),
            'MOS': (640, 320),
            'SEV': (720, 320),
            'RUM': (720, 400),
            'BUL': (720, 480),
            'SER': (640, 480),
            'BUD': (560, 560),
            'TRI': (560, 640),
            'TYR': (480, 640),
            'ALB': (640, 560),
            'GRE': (720, 560),
            'CON': (720, 640),
            'ANK': (720, 720),
            'SMY': (640, 720),
            'SYR': (560, 720),
            'ARM': (640, 640),
            'ADR': (560, 720),
            'AEG': (640, 640),
            'BAR': (560, 240),
            'BLA': (720, 560),
            'EAS': (640, 640),  # Eastern Mediterranean
            'ENG': (240, 480),  # English Channel
            'HEL': (400, 400),  # Heligoland Bight
            'ION': (640, 720),  # Ionian Sea
            'IRI': (160, 400),  # Irish Sea
            'MAO': (80, 640),   # Mid-Atlantic Ocean
            'NAO': (80, 320),   # North Atlantic Ocean
            'NTH': (320, 320),  # North Sea
            'WES': (480, 720)   # Western Mediterranean
    
            # ... Add the remaining territory positions here ...

        }
        return positions.get(position, (0, 0))

    def cmdloop(self, intro=None):
      self.preloop()
      self.intro = intro
      if self.intro:
          self.stdout.write(str(self.intro)+"\n")
      stop = None
      while not stop:
          # Pygame Event Loop (Moved to the top to ensure immediate response)
          for event in pygame.event.get():
              if event.type == pygame.QUIT:
                  pygame.quit()
                  sys.exit()
  
          # Draw the game board
          self.draw_board()
  
          # Update the display
          pygame.display.flip()
  
          # Cmd Event Loop
          if self.cmdqueue:
              line = self.cmdqueue.pop(0)
          else:
              self.stdout.write(self.prompt)
              self.stdout.flush()
              line = input()
          line = self.precmd(line)
          stop = self.onecmd(line)
          stop = self.postcmd(stop, line)
      
      self.postloop()

if __name__ == '__main__':
    DiplomacyPlus().cmdloop()
