import random
import numpy as np
import matplotlib.pyplot as plt

def get_valid_int(prompt, min_val=None, max_val=None):
    while True:
        user_input = input(prompt)
        try:
            num = int(user_input)
            if (min_val is not None and num < min_val) or (max_val is not None and num > max_val):
                print(f"Please enter a number between {min_val} and {max_val}.")
            else:
                return num
        except ValueError:
            print("Invalid input. Please enter a valid integer.")

def get_valid_choice(prompt, choices):
    choices = [c.lower() for c in choices]
    while True:
        choice = input(prompt).strip().lower()
        if choice in choices:
            return choice
        print(f"Please enter one of the following: {', '.join(choices)}")

def draw_table_by_seat_with_ranks(players_with_seats, player_sit, ranked_list, filename='table_summary.png'):
    seat_positions = {1: (0.85, 0.5), 2: (0.5, 0.1), 3: (0.15, 0.5)}
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.set_facecolor('darkgreen')
    plt.axis('off')
    table = plt.Circle((0.5, 0.5), 0.4, color='darkgreen', zorder=0)
    ax.add_artist(table)
    ranking_map = {name: idx + 1 for idx, (name, _, _, _, _) in enumerate(ranked_list)}
    for seat, player in players_with_seats.items():
        name = player.name
        chips = player.chips
        is_human = seat == player_sit
        rank = ranking_map.get(name, '?')
        if is_human:
            label = f'You ({name})\n#{rank}\n{chips} chips'
            color = 'gold'
        else:  # inserted
            label = f'{name}\n#{rank}\n{chips} chips'
            color = 'blue' if seat!= player_sit and 'Bot1' in name else 'red'
        pos = seat_positions.get(seat, (0.5, 0.5))
        ax.text(pos[0], pos[1], label, ha='center', va='center', fontsize=10, bbox=dict(boxstyle='round', fc=color, ec='black'))
    plt.savefig(filename, bbox_inches='tight')
    plt.close()

class Card:
    def __init__(self, suit, rank):
        self.suit = suit
        self.rank = rank

    def __str__(self):
        return f'{self.rank}{self.suit}'

class Deck:
    def __init__(self, seed=None):
        self.suits = ['♠', '♥', '♦', '♣']
        self.ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
        self.cards = [Card(suit, rank) for suit in self.suits for rank in self.ranks]
        self.seed = seed
        if self.seed is not None:
            random.seed(self.seed)
        self.shuffle()

    def shuffle(self):
        random.shuffle(self.cards)

    def deal_card(self):
        if self.cards:
            return self.cards.pop(0)
        raise ValueError('The deck is empty.')

class Hand:
    def __init__(self):
        self.cards = []

    def add_card(self, card):
        self.cards.append(card)

    def reset(self):
        self.cards = []

    def get_value(self):
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
            for i in range(aces):
                if total >= 11:
                    total = total + 1
                elif i+1 == aces and total <= 10:
                    total = total + 11
        return total

class Player:
    def __init__(self, name, chips):
        self.name = name
        self.chips = chips
        self.hand = Hand()
        self.bet = 0
        self.total_chips_added = chips

    def __str__(self):
        return f'{self.name} now has {self.chips} chips.'

    def place_bet(self, amount):
        if amount > self.chips:
            raise ValueError('Not enough chips to place this bet.')
        self.bet = amount
        self.chips = self.chips - amount

    def add_card(self, card):
        self.hand.add_card(card)

    def has_bust(self):
        return self.hand.get_value() > 21

    def reset_hand(self):
        self.hand.reset()
        self.bet = 0

class BotPlayer(Player):
    def __init__(self, name, chips, seed):
        super().__init__(name, chips)
        self.seed = seed
        self.rng = random.Random(seed)

    def decide_move(self):
        if self.hand.get_value() < 17:
            return 'hit'
        return 'stand'

    def place_random_bet(self, min_bet=1):
        max_bet = self.chips
        return self.rng.randint(min_bet, max_bet)

class Dealer(Player):
    def __init__(self):
        super().__init__('Dealer', chips=0)
        self.hidden_card = None

    def set_hidden_card(self, card):
        self.hidden_card = card
        self.hand.add_card(card)

    def reveal_hidden_card(self):
        return self.hidden_card

    def should_draw(self):
        return self.hand.get_value() < 17

class GameManager:
    def __init__(self, player_name, player_chips, player_sit, deck_seed):
        self.deck = Deck(seed=deck_seed)
        self.player = Player(player_name, player_chips)
        self.bots = []
        self.dealer = Dealer()
        self.player_sit = player_sit

    def load_players_from_file(self, filepath):
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
        print('Welcome to Blackjack!')
        print('Nothing is left to chance when you are an engineer.')
        deck_seed = get_valid_int('Enter a seed value for the game: ')
        self.deck = Deck(seed=deck_seed)
        while True:
            print(f'\n{self.player.name}, you have {self.player.chips} chips.')
            if self.player.chips == 0:
                choice = get_valid_choice('You have no chips left. Do you want to buy more? (yes/no): ', ['yes', 'no'])
                if choice == 'yes':
                    amount = get_valid_int('Enter amount of chips to add: ', min_val=100, max_val=1000)
                    self.player.chips = amount
                    self.player.total_chips_added = amount
                else:  # inserted
                    print('You chose to leave the table.')
                    break
            play = get_valid_choice('Do you want to play a round? (yes/no): ', ['yes', 'no'])
            if play!= 'yes':
                print('You chose to leave the table.')
                break
            self.player.reset_hand()
            self.dealer.reset_hand()
            for bot in self.bots:
                bot.reset_hand()
            self.handle_bets()
            self.play_round()
            self.resolve_results()
            if len(self.deck.cards) <= 20:
                self.deck.cards = [Card(suit, rank) for suit in self.deck.suits for rank in self.deck.ranks]
                self.deck.shuffle()
        self.show_summary()
#TODO- fix error self.bots[bot_turn].add_card(self.deck.deal_card()) list index out of range
    def play_round(self):
        print()
        num_players = len(self.bots) + 1
        for t in range(2):
            bot_turn = 0
            for i in range(num_players):
                if (self.player_sit - 1) == i:
                    self.player.add_card(self.deck.deal_card())
                elif bot_turn < len(self.bots):
                    self.bots[bot_turn].add_card(self.deck.deal_card())
                    bot_turn = bot_turn + 1
            if t == 0:
                self.dealer.add_card(self.deck.deal_card())
            else:
                hidden = self.deck.deal_card()
                self.dealer.set_hidden_card(hidden)
        bot_turn = 0
        for i in range(num_players):
            if (self.player_sit - 1) == i:
                print(f'You got: {[str(card) for card in self.player.hand.cards]} (value: {self.player.hand.get_value()})')
            else:
                print(f'{self.bots[bot_turn].name} hand: {[str(card) for card in self.bots[bot_turn].hand.cards]} (value: {self.bots[bot_turn].hand.get_value()})')
                bot_turn = bot_turn + 1
        print(f'\nDealer shows: {self.dealer.hand.cards[0]}')
        bot_turn = 0
        for i in range(num_players):
            if (self.player_sit - 1) == i:
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
                print(f'\n{self.bots[bot_turn].name}\'s turn:')
                while not self.bots[bot_turn].has_bust() and self.bots[bot_turn].decide_move() == 'hit':
                    card = self.deck.deal_card()
                    self.bots[bot_turn].add_card(card)
                    print(f'{self.bots[bot_turn].name} draws: {card}')
                print(f'{self.bots[bot_turn].name} stands. Hand: {[str(c) for c in self.bots[bot_turn].hand.cards]} (value: {self.bots[bot_turn].hand.get_value()})')
                bot_turn = bot_turn + 1
        print(f'\nDealer reveals hidden card: {self.dealer.reveal_hidden_card()}')
        print(f'Dealer\'s hand: {[str(card) for card in self.dealer.hand.cards]} (value: {self.dealer.hand.get_value()})')
        while self.dealer.should_draw():
            card = self.deck.deal_card()
            self.dealer.add_card(card)
            print(f'Dealer draws a: {card}')
            print(f'Dealer now has: {[str(c) for c in self.dealer.hand.cards]} (value: {self.dealer.hand.get_value()})')

    def handle_bets(self):
        amount = get_valid_int(f'{self.player.name}, enter your bet (1 - {self.player.chips}): ', 1, self.player.chips)
        self.player.place_bet(amount)
        print(self.player)
        for bot in self.bots:
            if bot.chips == 0:
                rebuy = bot.total_chips_added
                bot.chips = rebuy
                bot.total_chips_added = bot.total_chips_added + rebuy
                print(f'{bot.name} was out of chips and added {rebuy} more chips.')
            amount = bot.place_random_bet()
            bot.place_bet(amount)
            print(f'{bot.name} bets {amount} chips and now has {bot.chips} chips.')

    def resolve_results(self):
        dealer_value = self.dealer.hand.get_value()
        dealer_bust = dealer_value > 21
        player_value = self.player.hand.get_value()
        print(f'\nYour final hand value: {player_value}')
        if self.player.has_bust():
            print('You busted and lost your bet.')
        else:
            if dealer_bust or player_value > dealer_value:
                self.player.chips =  self.player.chips + (self.player.bet * 2)
                print(f'You win! You now have {self.player.chips} chips.')
            else:
                if player_value == dealer_value:
                    self.player.chips = self.player.chips + self.player.bet
                    print(f'It\'s a tie. You get your bet back. Total chips: {self.player.chips}')
                else:
                    print('You lost this round.')
        for bot in self.bots:
            bot_value = bot.hand.get_value()
            result = ''
            if bot.has_bust():
                result = 'busted and lost.'
            else:
                if dealer_bust or bot_value > dealer_value:
                    bot.chips = bot.chips + (bot.bet * 2)
                    result = f'won and now has {bot.chips} chips.'
                else:
                    if bot_value == dealer_value:
                        bot.chips = bot.chips + bot.bet
                        result = f'tied and got their bet back. Total: {bot.chips} chips.'
                    else:
                        result = 'lost this round.'
            print(f'{bot.name} had {bot_value} → {result}')

    def show_summary(self):
        print('\n--- Game Summary ---')
        all_players = [self.player] + self.bots
        chip_counts = [p.chips for p in all_players]
        chip_ratios = []
        for p in all_players:
            initial = p.total_chips_added #if hasattr(p, 'total_chips_added') else p.chips
            ratio = round(p.chips / initial, 2)
            chip_ratios.append((p.name, p.chips, initial, ratio))
        names = [p.name for p in all_players]
        avg = np.mean(chip_counts)
        max_chips = np.max(chip_counts)
        for name, chips in zip(names, chip_counts):
            print(f'{name}: {chips} chips')
        print(f'\nAverage chips: {avg:.2f}')
        print(f'Highest chip count: {max_chips}')
        print('\nPlayer ranking (highest to lowest):')
        ranked = sorted(chip_ratios, key=lambda x: x[3], reverse=True)
        for i, (name, chips, invested, ratio) in enumerate(ranked, 1):
            print(f'{i}. {name} - Chips: {chips}, Invested: {invested}, Return Rate: {ratio}')
        players_by_seat = {}
        bot_index = 0
        for seat in range(1, 4):
            if seat == self.player_sit:
                players_by_seat[seat] = self.player
            else:
                players_by_seat[seat] = self.bots[bot_index]
                bot_index = bot_index + 1
        ranked = sorted([(p.name, p.chips, p.total_chips_added, p.chips + p.total_chips_added if p.total_chips_added else 0, p == self.player) for p in [self.player] + self.bots], key=lambda x: x[3], reverse=True)
        draw_table_by_seat_with_ranks(players_by_seat, self.player_sit, ranked)
        print('Table image with seating and rankings saved as \'table_summary.png\'')

if __name__ == '__main__':
    name = input('Enter your name: ')
    initial_chips = get_valid_int('Enter the amount of chips: ', min_val=100, max_val=1000)
    sit = get_valid_int('Where would you like to sit? (Choose a seat number from 1 to 3): ', min_val=1, max_val=3)
    game = GameManager(name, initial_chips, sit, deck_seed=0)
    game.load_players_from_file('bots.txt')
    game.start_game()
    input('\nPress Enter to exit...')