import random
import numpy as np
import matplotlib.pyplot as plt

# --- Utility Functions ---

def get_valid_int(prompt, min_val=None, max_val=None):
    """
    Prompts the user for an integer input and validates it.
    Ensures the input is a valid integer and optionally within a specified range.
    Args:
        prompt (str): The message to display to the user.
        min_val (int, optional): The minimum allowed value. Defaults to None.
        max_val (int, optional): The maximum allowed value. Defaults to None.
    Returns:
        int: The validated integer from the user.
    """
    while True:
        user_input = input(prompt)
        try:
            num = int(user_input)
            # Check if the number is within the specified min/max bounds
            if (min_val is not None and num < min_val) or (max_val is not None and num > max_val):
                print(f"Please enter a number between {min_val} and {max_val}.")
            else:
                return num
        except ValueError:
            print("Invalid input. Please enter a valid integer.")

def get_valid_choice(prompt, choices):
    """
    Prompts the user for a choice from a predefined list and validates it.
    The comparison is case-insensitive.
    Args:
     prompt (str): The message to display to the user.
     choices (list of str): A list of valid choices.
    Returns:
     str: The validated user choice in lowercase.
    """
    choices = [c.lower() for c in choices]
    while True:
        choice = input(prompt).strip().lower()
        if choice in choices:
            return choice
        print(f"Please enter one of the following: {', '.join(choices)}")

def draw_table_by_seat_with_ranks(players_with_seats, player_sit, ranked_list, filename='table_summary.png'):
    """
    Generates and saves a visual representation of the game table using matplotlib.
    It shows each player, their chip count, and their rank at their chosen seat.
    Args:
        players_with_seats (dict): A dictionary mapping seat number to Player objects.
        player_sit (int): The seat number of the human player.
        ranked_list (list): A sorted list of player data used to determine ranks.
        filename (str): The name of the file to save the image as.
    """
    # Define fixed positions for seats to ensure consistent layout
    seat_positions = {1: (0.85, 0.5), 2: (0.5, 0.1), 3: (0.15, 0.5)}
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.set_facecolor('seagreen')
    plt.axis('off')# Hide the axis for a cleaner look

    # Draw the green table circle
    table = plt.Circle((0.5, 0.5), 0.4, color='seagreen', zorder=0)
    ax.add_artist(table)

    # Create a mapping from player name to their rank for easy lookup
    ranking_map = {name: idx + 1 for idx, (name, _, _, _, _) in enumerate(ranked_list)}

    # Iterate through seats and draw each player's information
    for seat, player in players_with_seats.items():
        name = player.name
        chips = player.chips
        is_human = seat == player_sit
        rank = ranking_map.get(name, '?') # Get rank, default to '?' if not found

        # Customize label and color for the human player vs. bots
        if is_human:
            label = f'You ({name})\n#{rank}\n{chips} chips'
            color = 'gold'
        else:
            label = f'{name}\n#{rank}\n{chips} chips'
            # Differentiate between the two bots by color
            color = 'blue' if seat!= player_sit and 'Bot1' in name else 'red'

        pos = seat_positions.get(seat, (0.5, 0.5))
        ax.text(pos[0], pos[1], label, ha='center', va='center', fontsize=10,
                bbox=dict(boxstyle='round', fc=color, ec='black'))

    plt.savefig(filename, bbox_inches='tight')
    plt.close()

# --- Core Game Classes ---

class Card:
    """Represents a single playing card with a suit and a rank."""
    def __init__(self, suit, rank):
        self.suit = suit
        self.rank = rank

    def __str__(self):
        """Provides a simple string representation of the card, e.g., 'K♠'."""
        return f'{self.rank}{self.suit}'

class Deck:
    """Represents a deck of 52 playing cards."""
    def __init__(self, seed=None):
        self.suits = ['♠', '♥', '♦', '♣']
        self.ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
        self.cards = [Card(suit, rank) for suit in self.suits for rank in self.ranks]
        self.seed = seed
        # If a seed is provided, use it for the random number generator for reproducible shuffles.
        if self.seed is not None:
            random.seed(self.seed)
        self.shuffle()

    def shuffle(self):
        """Shuffles the deck of cards."""
        random.shuffle(self.cards)

    def deal_card(self):
        """Removes and returns the top card from the deck."""
        if self.cards:
            return self.cards.pop(0)
        raise ValueError('The deck is empty.')

class Hand:
    """Represents the cards held by a player the dealer or the bots."""
    def __init__(self):
        self.cards = []

    def add_card(self, card):
        """Adds a card to the hand."""
        self.cards.append(card)

    def reset(self):
        """Clears all cards from the hand."""
        self.cards = []

    def get_value(self):
        """
        Calculates and returns the total value of the hand.
        It correctly handles the value of Aces (as 1 or 11).
        """
        total = 0
        aces = 0
        for card in self.cards:
            if card.rank == 'A':
                aces = aces + 1
            else:
                if card.rank in ['J', 'Q', 'K']:
                    total = total + 10
                else:
                    total = total + int(card.rank)

        # Handle aces: add them as 11 if possible without busting, otherwise as 1.
        for i in range(aces):
            if total + 11 <= 21 - (aces - 1):
                total += 11
            else:
                total += 1
        return total

class Player:
    """A base class representing a player at the table."""
    def __init__(self, name, chips):
        self.name = name
        self.chips = chips
        self.hand = Hand()
        self.bet = 0
        self.total_chips_added = chips

    def __str__(self):
        """String representation of the player's current status."""
        return f'{self.name} now has {self.chips} chips.'

    def place_bet(self, amount):
        """Places a bet, deducting the amount from the player's chips."""
        if amount > self.chips:
            raise ValueError('Not enough chips to place this bet.')
        self.bet = amount
        self.chips = self.chips - amount

    def add_card(self, card):
        """Adds a card to the player's hand."""
        self.hand.add_card(card)

    def has_bust(self):
        """Checks if the player's hand value is over 21."""
        return self.hand.get_value() > 21

    def reset_hand(self):
        """Resets the player's hand and bet for a new round."""
        self.hand.reset()
        self.bet = 0

class BotPlayer(Player):
    """Represents an AI-controlled player with a simple, fixed strategy."""
    def __init__(self, name, chips, seed):
        super().__init__(name, chips)
        self.seed = seed
        self.rng = random.Random(seed)

    def decide_move(self):
        """
        A simple AI strategy: hit if hand value is less than 17, otherwise stand.
        This is a common "basic strategy" rule.
        """
        if self.hand.get_value() < 17:
            return 'hit'
        return 'stand'

    def place_random_bet(self, min_bet=1):
        """Places a random bet between a minimum value and all their chips."""
        max_bet = self.chips
        return self.rng.randint(min_bet, max_bet)

class Dealer(Player):
    """Represents the dealer, with special rules for playing their hand."""
    def __init__(self):
        super().__init__('Dealer', chips=0)
        self.hidden_card = None

    def set_hidden_card(self, card):
        """Sets the dealer's face-down card."""
        self.hidden_card = card
        self.hand.add_card(card)

    def reveal_hidden_card(self):
        """Returns the dealer's hidden card when it's time to reveal it."""
        return self.hidden_card

    def should_draw(self):
        """The dealer's rule: must draw until their hand value is 17 or more."""
        return self.hand.get_value() < 17

class GameManager:
    """Manages the overall flow of the Blackjack game."""
    def __init__(self, player_name, player_chips, player_sit, deck_seed):
        self.deck = Deck(seed=deck_seed)
        self.player = Player(player_name, player_chips)
        self.bots = []
        self.dealer = Dealer()
        self.player_sit = player_sit

    def load_players_from_file(self, filepath):
        """Loads bot player data from a text file."""
        self.bots = []
        try:
            with open(filepath, 'r') as file:
                for line in file:
                    parts = line.strip().split(',')
                    if len(parts) == 3:
                        name = parts[0]
                        chips = int(parts[1])
                        seed = int(parts[2])
                        self.bots.append(BotPlayer(name, chips, seed))
        except FileNotFoundError:
                print(f'File not found: {filepath}')
                return
        except ValueError:
                print('Invalid data format in player file.')
                return None
        for bot in self.bots:
            print(bot)

    def start_game(self):
        """Initiates and runs the main game loop."""
        print('Welcome to Blackjack!')
        print('Nothing is left to chance when you are an engineer.')

        deck_seed = get_valid_int('Enter a seed value for the game: ')
        self.deck = Deck(seed=deck_seed)

        # Main game loop
        while True:
            print(f'\n{self.player.name}, you have {self.player.chips} chips.')

            # Handle player running out of chips
            if self.player.chips == 0:
                choice = get_valid_choice('You have no chips left. Do you want to buy more? (yes/no): ', ['yes', 'no'])
                if choice == 'yes':
                    amount = get_valid_int('Enter amount of chips to add: ', min_val=100, max_val=1000)
                    self.player.chips = amount
                    self.player.total_chips_added += amount
                else:
                    print('You chose to leave the table.')
                    break

            # Ask if the player wants to continue playing
            play = get_valid_choice('Do you want to play a round? (yes/no): ', ['yes', 'no'])
            if play!= 'yes':
                print('You chose to leave the table.')
                break

            # Reset hands and bets for a new round
            self.player.reset_hand()
            self.dealer.reset_hand()
            for bot in self.bots:
                bot.reset_hand()

            self.handle_bets()
            self.play_round()
            self.resolve_results()

            # Reshuffle the deck if it's getting low on cards
            if len(self.deck.cards) <= 20:
                self.deck.cards = [Card(suit, rank) for suit in self.deck.suits for rank in self.deck.ranks]
                self.deck.shuffle()

        self.show_summary()

    def play_round(self):
        """Manages the logic for a single round of Blackjack."""
        print()
        num_players = len(self.bots) + 1

        # --- Dealing Phase ---
        # Deal two cards to each player and the dealer
        for t in range(2):
            # Deal to players in seat order
            bot_turn = 0
            for i in range(num_players):
                # Find which player is in the current seat
                if (self.player_sit - 1) == i:
                    self.player.add_card(self.deck.deal_card())
                elif bot_turn < len(self.bots):
                    # This logic assumes bots fill the other seats in order
                    self.bots[bot_turn].add_card(self.deck.deal_card())
                    bot_turn = bot_turn + 1

            # Dealer gets one card face up, one face down
            if t == 0:
                self.dealer.add_card(self.deck.deal_card())
            else:
                hidden = self.deck.deal_card()
                self.dealer.set_hidden_card(hidden)

        # --- Show Initial Hands ---
        bot_turn = 0
        for i in range(num_players):
            if (self.player_sit - 1) == i:
                print(f'You got: {[str(card) for card in self.player.hand.cards]} (value: {self.player.hand.get_value()})')
            else:
                print(f'{self.bots[bot_turn].name} hand: {[str(card) for card in self.bots[bot_turn].hand.cards]} (value: {self.bots[bot_turn].hand.get_value()})')
                bot_turn = bot_turn + 1
        print(f'\nDealer shows: {self.dealer.hand.cards[0]}')
        bot_turn = 0

        # --- Player Turns ---
        for i in range(num_players):
            if (self.player_sit - 1) == i:
                # Human player's turn
                print()
                while not self.player.has_bust():
                    move = get_valid_choice('Do you want to \'hit\' or \'stand\'? ', ['hit', 'stand'])
                    if move == 'hit':
                        card = self.deck.deal_card()
                        self.player.add_card(card)
                        print(f'You drew: {card}')
                        print(f'New hand: {[str(c) for c in self.player.hand.cards]} (value: {self.player.hand.get_value()})')
                    else:
                        if move == 'stand':
                            break
                        print('Invalid input. Please type \'hit\' or \'stand\'.')
            else:
                # Bots' turns
                print(f'\n{self.bots[bot_turn].name}\'s turn:')
                while not self.bots[bot_turn].has_bust() and self.bots[bot_turn].decide_move() == 'hit':
                    card = self.deck.deal_card()
                    self.bots[bot_turn].add_card(card)
                    print(f'{self.bots[bot_turn].name} draws: {card}')
                print(f'{self.bots[bot_turn].name} stands. Hand: {[str(c) for c in self.bots[bot_turn].hand.cards]} (value: {self.bots[bot_turn].hand.get_value()})')
                bot_turn = bot_turn + 1

        # --- Dealer's Turn ---
        print(f'\nDealer reveals hidden card: {self.dealer.reveal_hidden_card()}')
        print(f'Dealer\'s hand: {[str(card) for card in self.dealer.hand.cards]} (value: {self.dealer.hand.get_value()})')
        while self.dealer.should_draw():
            card = self.deck.deal_card()
            self.dealer.add_card(card)
            print(f'Dealer draws a: {card}')
            print(f'Dealer now has: {[str(c) for c in self.dealer.hand.cards]} (value: {self.dealer.hand.get_value()})')

    def handle_bets(self):
        """Collects bets from the human player and the bots."""
        # Player's bet
        amount = get_valid_int(f'{self.player.name}, enter your bet (1 - {self.player.chips}): ', 1, self.player.chips)
        self.player.place_bet(amount)
        print(self.player)

        # Bots' bets
        for bot in self.bots:
            # Rebuy logic for bots
            if bot.chips == 0:
                rebuy = bot.total_chips_added
                bot.chips = rebuy
                bot.total_chips_added = bot.total_chips_added + rebuy
                print(f'{bot.name} was out of chips and added {rebuy} more chips.')

            amount = bot.place_random_bet()
            bot.place_bet(amount)
            print(f'{bot.name} bets {amount} chips and now has {bot.chips} chips.')

    def resolve_results(self):
        """Determines the outcome for each player and settles bets."""
        dealer_value = self.dealer.hand.get_value()
        dealer_bust = dealer_value > 21

        # Resolve player's outcome
        player_value = self.player.hand.get_value()
        print(f'\nYour final hand value: {player_value}')
        if self.player.has_bust():
            print('You busted and lost your bet.')
        elif dealer_bust or player_value > dealer_value:
            self.player.chips =  self.player.chips + (self.player.bet * 2)
            print(f'You win! You now have {self.player.chips} chips.')
        elif player_value == dealer_value:
            self.player.chips = self.player.chips + self.player.bet
            print(f'It\'s a tie. You get your bet back. Total chips: {self.player.chips}')
        else:
            print('You lost this round.')

        # Resolve bots' outcomes
        for bot in self.bots:
            bot_value = bot.hand.get_value()
            result = ''
            if bot.has_bust():
                result = 'busted and lost.'
            elif dealer_bust or bot_value > dealer_value:
                bot.chips = bot.chips + (bot.bet * 2)
                result = f'won and now has {bot.chips} chips.'
            elif bot_value == dealer_value:
                bot.chips = bot.chips + bot.bet
                result = f'tied and got their bet back. Total: {bot.chips} chips.'
            else:
                result = 'lost this round.'

            print(f'{bot.name} had {bot_value} → {result}')

    def show_summary(self):
        """Displays the final game summary and statistics."""
        print('\n--- Game Summary ---')
        all_players = [self.player] + self.bots
        chip_counts = [p.chips for p in all_players]
        chip_ratios = []

        # Create a list of tuples with all data needed for ranking
        for p in all_players:
            initial = p.total_chips_added
            ratio = f"{(p.chips / initial):.2f}"
            chip_ratios.append((p.name, p.chips, initial, ratio))
        names = [p.name for p in all_players]
        avg = np.mean(chip_counts)
        max_chips = np.max(chip_counts)
        for name, chips in zip(names, chip_counts):
            print(f'{name}: {chips} chips')
        print(f'\nAverage chips: {avg:.2f}')
        print(f'Highest chip count: {max_chips}')
        print('\nPlayer ranking (highest to lowest):')

        # Sort players by their return on investment (ratio)
        ranked = sorted(chip_ratios, key=lambda x: x[3], reverse=True)
        for i, (name, chips, invested, ratio) in enumerate(ranked, 1):
            print(f'{i}. {name} - Chips: {chips}, Invested: {invested}, Return Rate: {ratio}')

        # Prepare data for the table visualization
        players_by_seat = {}
        bot_index = 0
        for seat in range(1, 4):
            if seat == self.player_sit:
                players_by_seat[seat] = self.player
            else:
                players_by_seat[seat] = self.bots[bot_index]
                bot_index = bot_index + 1
        ranked = sorted(
            [
                (
                    p.name,
                    p.chips,
                    p.total_chips_added,
                    p.chips / p.total_chips_added if p.total_chips_added else 0, p == self.player) for p in [self.player] + self.bots
            ],
            key=lambda x: x[3], reverse=True
        )

        # Generate and save the summary image
        draw_table_by_seat_with_ranks(players_by_seat, self.player_sit, ranked)
        print('Table image with seating and rankings saved as \'table_summary.png\'')

if __name__ == '__main__':
    # --- Game Setup ---
    # This block runs when the script is executed directly.
    # It collects initial information from the user to set up the game.
    name = input('Enter your name: ')
    initial_chips = get_valid_int('Enter the amount of chips: ', min_val=100, max_val=1000)
    sit = get_valid_int('Where would you like to sit? (Choose a seat number from 1 to 3): ', min_val=1, max_val=3)

    # Instantiate the main game controller
    game = GameManager(name, initial_chips, sit, deck_seed=0)

    # Load bot players from an external file
    game.load_players_from_file('bots.txt')

    # Start the game
    game.start_game()