import sqlite3
from typing import Tuple, Dict


# Simple function that creates a connection with a filename given and returns a connection and cursor.
def open_db(filename: str) -> Tuple[sqlite3.Connection, sqlite3.Cursor]:
    connection = sqlite3.connect(filename)  # Connects to an existing database or creates a new one.
    cursor = connection.cursor()  # We are now ready to read/write data.
    return connection, cursor


# Simple function that closes a database.
def close_db(connection: sqlite3.Connection):
    connection.close()


# Simple function that creates the initial table foods with its respective columns.
def create_table(connection: sqlite3.Connection, cursor: sqlite3.Cursor):
    cursor.execute('''CREATE TABLE IF NOT EXISTS foods(
                       Food TEXT NOT NULL PRIMARY KEY,
                       Calories INT NOT NULL,
                       Protein INT NOT NULL,
                       Fat INT NOT NULL,
                       Carbohydrate INT NOT NULL
                       );''')
    connection.commit()


def food_entry() -> Dict:
    while True:
        foodName = input("Please enter in the food's name>>").lower().capitalize()
        calories = int(input("Please enter in the food's calories>>"))
        proteinAmount = int(input("Please enter in the food's protein amount>>"))
        carbohydrateAmount = int(input("Please enter in the food's carbohydrate amount>>"))
        fatAmount = int(input("Please enter in the food's fat amount>>"))

        lowerLimit = fatAmount * 9 + carbohydrateAmount * 4 + proteinAmount * 4 - 3
        upperLimit = fatAmount * 9 + carbohydrateAmount * 4 + proteinAmount * 4 + 3
        if not lowerLimit < calories < upperLimit:
            print("The calories don't seem right for the macro-nutrients. "
                  "Disregarding this entry and restarting...\n")
            continue

        print("\nHere's what you entered:\nFood: {}\nCalories: {}\nProtein: {}\nCarbohydrates: {}\nFat: {}".format(
            foodName, calories, proteinAmount, carbohydrateAmount, fatAmount))
        answer = input("Is this the correct information? Type 'y' or 'n'>>").lower()

        if answer == 'y':
            return {"food": foodName, "calories": calories, "protein": proteinAmount,
                    "carbohydrate": carbohydrateAmount, "fat": fatAmount}
        else:
            print("Disregarding this entry and restarting...\n")


def save_to_database(food: Dict, connection: sqlite3.Connection, cursor: sqlite3.Cursor):
    try:
        cursor.execute("INSERT INTO foods VALUES (?, ?, ?, ?, ?);",
                       [food['food'],
                        food['calories'],
                        food['protein'],
                        food['fat'],
                        food['carbohydrate']
                        ])
        print("Successfully saved to database.")
    except sqlite3.IntegrityError:
        pass
    connection.commit()


def main():
    connection, cursor = open_db("nutrition.db")
    create_table(connection, cursor)
    save_to_database(food_entry(), connection, cursor)

    close_db(connection)


if __name__ == "__main__":
    main()
