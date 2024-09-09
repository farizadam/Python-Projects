
import random
import sys
import sqlite3

random.seed()

# Connect to SQLite database
conn = sqlite3.connect('card.s3db')
cur = conn.cursor()

# Create table if it doesn't exist
cur.execute("""
CREATE TABLE IF NOT EXISTS card (
    id INTEGER PRIMARY KEY,
    number TEXT UNIQUE,
    pin TEXT,
    balance INTEGER DEFAULT 0
);
""")
conn.commit()

class Card:
    def __init__(self):
        self.card = ''
        self.pin = ''
        self.login_card = ''
        self.login_pin = ''
        self.row = []
        self.balance = 0
        self.receiver_balance = 0
        
    def create_account(self):
        try:
            print("Your card has been created")
            print("Your card number:")
            self.card = self.generate_card_number()  # Changed: Used generate_card_number method for card number
            print(self.card)
            print("Your card PIN:")
            self.pin = str(random.randint(1000, 9999))
            print(self.pin)
            # Changed: Parameterized query to prevent SQL injection
            cur.execute("INSERT INTO card (number, pin) VALUES (?, ?);", (self.card, self.pin))
            conn.commit()
        except sqlite3.Error as e:
            print(f"An error occurred: {e}")  # Changed: Added error handling

    def log_in(self):
        self.login_card = input("Enter your card number:\n")
        self.login_pin = input("Enter your PIN:\n")
        
        try:
            # Changed: Parameterized query to prevent SQL injection
            cur.execute("SELECT id, number, pin, balance FROM card WHERE number = ? AND pin = ?", (self.login_card, self.login_pin))
            self.row = cur.fetchone()
            if self.row:
                self.balance = self.row[3]
                print('\nYou have successfully logged in')
                self.success()
            else:
                print("Wrong card number or PIN")
        except sqlite3.Error as e:
            print(f"An error occurred: {e}")  # Changed: Added error handling
            
    def success(self):
        while True:
            print("""\n1. Balance
2. Add income
3. Do transfer
4. Close account
5. Log out
0. Exit""")
            i = int(input())
            if i == 1:
                print('\nBalance: ', self.balance)
            elif i == 2:
                self.add_income()  # Changed: Moved income addition logic to a separate method
            elif i == 3:
                self.do_transfer()  # Changed: Moved transfer logic to a separate method
            elif i == 4:
                self.close_account()  # Changed: Moved account closure logic to a separate method
                break
            elif i == 5:
                print("\nYou have successfully logged out!")
                break
            elif i == 0:
                print("\nBye!")
                conn.close()
                sys.exit()
            else:
                print("Invalid input")

    def add_income(self):
        try:
            print('\nEnter income:')
            amount = int(input())
            if amount > 0:  # Changed: Added validation for income amount
                self.balance += amount
                # Changed: Parameterized query to prevent SQL injection
                cur.execute("UPDATE card SET balance = ? WHERE number = ?", (self.balance, self.login_card))
                conn.commit()
                print('Income was added!')
            else:
                print("Invalid amount!")
        except ValueError:
            print("Invalid input. Please enter a number.")  # Changed: Added error handling for invalid input
        except sqlite3.Error as e:
            print(f"An error occurred: {e}")  # Changed: Added error handling

    def do_transfer(self):
        try:
            print('\nTransfer\nEnter card number:')
            receiver_card = input()
            if not self.luhn_check(receiver_card):  # Changed: Used luhn_check for validation
                print('Probably you made a mistake in the card number. Please try again!')
                return

            # Changed: Parameterized query to prevent SQL injection
            cur.execute("SELECT id, number, pin, balance FROM card WHERE number = ?", (receiver_card,))
            receiver = cur.fetchone()
            if not receiver:
                print('Such a card does not exist.')
                return

            print("Enter how much money you want to transfer:\n")
            transfer_amount = int(input())
            if transfer_amount <= 0:  # Changed: Added validation for transfer amount
                print("Invalid amount!")
            elif transfer_amount > self.balance:
                print("Not enough money!")
            else:
                self.balance -= transfer_amount
                # Changed: Parameterized query to prevent SQL injection
                cur.execute("UPDATE card SET balance = ? WHERE number = ?", (self.balance, self.login_card))
                self.receiver_balance = receiver[3] + transfer_amount
                # Changed: Parameterized query to prevent SQL injection
                cur.execute("UPDATE card SET balance = ? WHERE number = ?", (self.receiver_balance, receiver_card))
                conn.commit()
                print("Success!")
        except ValueError:
            print("Invalid input. Please enter a number.")  # Changed: Added error handling for invalid input
        except sqlite3.Error as e:
            print(f"An error occurred: {e}")  # Changed: Added error handling

    def close_account(self):
        try:
            # Changed: Parameterized query to prevent SQL injection
            cur.execute("DELETE FROM card WHERE number = ?", (self.login_card,))
            conn.commit()
            print('\nThe account has been closed!')
        except sqlite3.Error as e:
            print(f"An error occurred: {e}")  # Changed: Added error handling

    def luhn_check(self, num):
        def digits_of(n):
            return [int(d) for d in str(n)]
        
        digits = digits_of(num)
        odd_digits = digits[-1::-2]
        even_digits = digits[-2::-2]
        checksum = sum(odd_digits)
        
        for d in even_digits:
            doubled = d * 2
            checksum += doubled if doubled < 10 else doubled - 9
        
        return checksum % 10 == 0

    def generate_card_number(self):
        num = '400000' + str(random.randint(100000000, 999999999))
        check_digit = 0
        while not self.luhn_check(num + str(check_digit)):
            check_digit += 1
        return num + str(check_digit)
    
    def menu(self):
        while True:
            print("""\n1. Create an account
2. Log into account
0. Exit""")
            i = int(input())
            if i == 1:
                self.create_account()
            elif i == 2:
                self.log_in()
            elif i == 0:
                conn.close()
                print("\nBye!")
                break
            else:
                print("Invalid input")

# Create a Card object and run the menu
card = Card()
card.menu()
