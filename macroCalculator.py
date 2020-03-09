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
                       Carbohydrate INT NOT NULL,
                       Fiber INT NOT NULL
                       );''')
    connection.commit()


def return_food_entry(foodArg='') -> Dict:
    while True:
        if foodArg == '':
            foodName = input("Please enter in the food's name>>").lower().capitalize()
        else:
            foodName = foodArg.lower().capitalize()
        calories = int(input("Please enter in the food's calories>>"))
        proteinAmount = int(input("Please enter in the food's protein amount>>"))
        carbohydrateAmount = int(input("Please enter in the food's carbohydrate amount>>"))
        fatAmount = int(input("Please enter in the food's fat amount>>"))
        fiberAmount = int(input("Please enter in the food's fiber amount>>"))

        lowerLimit = fatAmount * 9 + carbohydrateAmount * 4 + proteinAmount * 4 - 10
        upperLimit = fatAmount * 9 + carbohydrateAmount * 4 + proteinAmount * 4 + 10
        if not lowerLimit < calories < upperLimit:
            print("The calories don't seem right for the macro-nutrients. "
                  "Disregarding this entry and restarting...\n")
            continue

        print("\nHere's what you entered:\nFood: {}\nCalories: {}\nProtein: {}\nCarbohydrates: {}\n"
              "Fat: {}\nFiber: {}".format(
               foodName, calories, proteinAmount, carbohydrateAmount, fatAmount, fiberAmount))
        answer = input("Is this the correct information? Type 'y' or 'n'>>").lower()

        if answer == 'y':
            return {"food": foodName, "calories": calories, "protein": proteinAmount,
                    "carbohydrate": carbohydrateAmount, "fat": fatAmount, "fiber": fiberAmount}
        else:
            print("Disregarding this entry and restarting...\n")


def save_to_database(food: Dict, connection: sqlite3.Connection, cursor: sqlite3.Cursor):
    try:
        cursor.execute("INSERT INTO foods VALUES (?, ?, ?, ?, ?, ?);",
                       [food['food'],
                        food['calories'],
                        food['protein'],
                        food['fat'],
                        food['carbohydrate'],
                        food['fiber']
                        ])
        print("Successfully saved to database.\n")
    except sqlite3.IntegrityError:
        print("{} data already exists. New food's data has not been saved.".format(food["food"]))
        pass
    connection.commit()


def delete_food(connection: sqlite3.Connection, cursor: sqlite3.Cursor, food: str):
    foodExists = False
    cursor.execute("SELECT * FROM FOODS WHERE FOODS.FOOD = ?", (food,))
    if cursor.fetchone() is not None:
        foodExists = True

    if not foodExists:
        print("Food information not found in database.")
        return

    cursor.execute("DELETE FROM FOODS WHERE FOODS.FOOD = ?", (food,))
    print("Food information successfully deleted from database.")
    connection.commit()


def track_macros(connection: sqlite3.Connection, cursor: sqlite3.Cursor):
    foodsEaten = []
    foodEaten = ''
    totalCalories = 0
    totalProtein = 0
    totalCarbohydrate = 0
    totalFat = 0
    totalFiber = 0

    while foodEaten != 'stop':
        addFood = ''
        foodEaten = input("Please type in a food that you have eaten or 'stop' to stop entering foods>>").lower()
        if foodEaten == 'stop':
            break

        cursor.execute("SELECT * FROM FOODS WHERE FOODS.FOOD = ?", (foodEaten.capitalize(),))
        result = cursor.fetchone()
        if result is None:
            print("This food does not exist in the database.")
            while addFood != 'n':
                addFood = input("Please type 'a' if you would like to add it to the database "
                                "or 'n' to continue adding other foods>>").lower()
                if addFood == 'a':
                    result = return_food_entry(foodArg=foodEaten)
                    save_to_database(result, connection, cursor)
                    totalCalories += result['Calories']
                    totalCarbohydrate += result['Carbohydrate']
                    totalFat += result['Fat']
                    totalProtein += result['Protein']
                    totalFiber += result['Fiber']
                    break
        else:
            totalCalories += result[1]
            totalProtein += result[2]
            totalFat += result[3]
            totalCarbohydrate += result[4]
            totalFiber += result[5]

        if addFood == 'n':
            continue

        foodsEaten.append(foodEaten)

    if len(foodsEaten) == 0:
        print("No foods were provided, so no information is available to display. Going back to main query...\n")
        return

    proteinPercentage = int(totalProtein * 4 * 100 / totalCalories)
    fatPercentage = int(totalFat * 9 * 100 / totalCalories)
    carbohydratePercentage = int(totalCarbohydrate * 4 * 100 / totalCalories)
    remainingPercentage = 100 - proteinPercentage - fatPercentage - carbohydratePercentage

    print("\nYou consumed the foods: {}.".format(", ".join(foodsEaten)))
    print("You ate a total of {} calories, {} grams of protein, {} grams of fat,"
          " {} grams of carbohydrates, and {} grams of fiber.".format(
           totalCalories, totalProtein, totalFat, totalCarbohydrate, totalFiber))
    print("{}% of calories from {} grams of protein.".format(proteinPercentage, totalProtein))
    print("{}% of calories from {} grams of fat.".format(fatPercentage, totalFat))
    print("{}% of calories from {} grams of carbohydrates.".format(carbohydratePercentage, totalCarbohydrate))
    print("{}% of calories are inaccurate from incorrect data.\n".format(abs(remainingPercentage)))


def main():
    connection, cursor = open_db("nutrition.db")
    create_table(connection, cursor)

    promptAnswer = ''

    while promptAnswer != 'stop':
        promptAnswer = input("Would you like to alter the database or track macros for the day? "
                             "Type 'a' to alter, 't' to track, or 'stop' to stop>>").lower()
        if promptAnswer == 'a':
            alterAnswer = input("How would you like to alter? Type 'd' to delete or 'a' to add information>>").lower()
            if alterAnswer == 'd':
                deleteAnswer = ""
                while deleteAnswer != 'stop':
                    deleteAnswer = input(
                        "What food would you like to delete? Type food name or 'stop' to stop>>").lower()
                    if deleteAnswer != "stop":
                        delete_food(connection, cursor, deleteAnswer.capitalize())
            elif alterAnswer == 'a':
                entryAnswer = ""
                while entryAnswer != 'n':
                    entry = return_food_entry()
                    save_to_database(entry, connection, cursor)
                    entryAnswer = input("\nWould you like to add another food?>> Type 'n' to stop "
                                        "or anything else to continue>>").lower()
        elif promptAnswer == 't':
            track_macros(connection, cursor)
        else:
            print("I did not quite get that. Please try again.\n")
    print("Goodbye. Have a nice day.")
    close_db(connection)


if __name__ == "__main__":
    main()
