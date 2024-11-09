#
#
# # pip install matplotlib !!!
#
# import matplotlib.pyplot as plt
# import numpy as np
#
# # Data
# labels = ['Correct', 'Wrong', 'Not Answered']
# sizes = [25, 35, 20]
# colors = ['yellowgreen', 'red', 'gold']
# explode = (0.1, 0, 0)  # To "explode" the first slice
#
# # Create a pie chart
# fig, ax = plt.subplots()
# ax.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%',
#        shadow=True, startangle=90)
#
# # Equal aspect ratio ensures that the pie chart is drawn as a circle.
# ax.axis('equal')
#
# # Add a headline
# ax.set_title("Distribution of Answers")
#
# # Show the plot
# plt.show()
##############################################
import time
import itertools
from datetime import datetime
from time import sleep
import psycopg2
import psycopg2.extras
from pymongo import MongoClient
import bcrypt
from random import sample



#from w import age_group

connection = psycopg2.connect(
        host="localhost",
        database="postgres",
        user="postgres",
        password="admin",
        port="5432"
    )
pg_cursor = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)

# Connect to MongoDB
# mongo_client = MongoClient('mongodb://localhost:27017/')
# mongo_db = mongo_client["Trivia_MongoDB"]
# questions_collection = mongo_db['questions']
client = MongoClient("mongodb://localhost:27017/")
mongo_db = client["Trivia_MongoDB"]
questions_collection = mongo_db["questions"]
player_questions_collection = mongo_db['player_questions']






# sample_questions = questions_collection.find().limit(5)
# for question in sample_questions:
#     print(question)
# print(questions_collection.find_one({"Question_No": 496}))
# pg_cursor.execute("SELECT question_id FROM most_least_answered_questions() LIMIT 10;")
# results = pg_cursor.fetchall()
# for row in results:
#     print(row['question_id'])

#
# sample_questions = questions_collection.find().limit(5)
# for question in sample_questions:
#     print(question)

colors = [


        "\033[91m",  # Red
        "\033[92m",  # Green
        "\033[33m",  # Yellow
        "\033[94m",  # Blue
        "\033[95m",  # Magenta
        "\033[96m",  # Cyan
    ]
reset = "\033[0m"  # Reset color to default

# Procedure to insert a new player

def insert_new_player(username, password, email, age):
    """Inserting a record for a new player in the PostgreSQL database upon registering"""
    while True:
        try:
            hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode('utf-8')

            # Use SELECT to call the function and retrieve the OUT parameter
            new_player_query = """
            SELECT * FROM new_player(%s, %s, %s, %s);
            """
            pg_cursor.execute(new_player_query, (username, hashed_password, email, age))
            result = pg_cursor.fetchone()
            if result:
                player_id = result[0]  # This assumes the first element is the player_id (OUT parameter)
                connection.commit()
                return player_id
                # else:
                # print("No player ID was returned.")
                # return None
        except psycopg2.Error as e:
            connection.rollback()
            error_message = str(e)

            print(f"An error occurred: {error_message}")
            if 'username' in error_message:
                username = input("This username already exists. Please enter a new one:")
            elif 'password' in error_message:
                password = input("This password already exists. Please enter a new one:")
            elif 'email' in error_message:
                email = input("This email already exists. Please enter a new one:")
            else:
                print("An unexpected error occurred", e)
                return None



# def fetch_random_questions(age, selected_topics):
#     age_group = get_age_group(age)
#     questions = list(questions_collection.find({"Age_Group": age_group, "Topic": {"$in": selected_topics}}))
#
#     print("Fetched Questions:", questions)  # Debugging print to check fetched questions
#
#     return sample(questions, min(len(questions), 20))


def create_player_questions_set(player_id, age_group, selected_topics):
    """Creates a unique set of 20 random questions for a player's quiz according to their age and selected topics."""

    # Step 1: Fetch the relevant questions
    questions = list(questions_collection.find({"Age_Group": age_group, "Topic": {"$in": selected_topics}}))
    player_questions = sample(questions, min(len(questions), 20))

    # Step 2: Prepare each question for insertion into player_questions_collection
    questions_for_session = [
        {
            "player_id": player_id,
            "Question_No": question["Question_No"],
            "Question_Text": question["Question_Text"],
            "Answer_a": question["Answer_a"],
            "Answer_b": question["Answer_b"],
            "Answer_c": question["Answer_c"],
            "Answer_d": question["Answer_d"],
            "Correct_Answer": question["Correct_Answer"],
            "Topic": question["Topic"],
            "Age_Group": question["Age_Group"],
            "is_answered": False  # Adding the is_answered flag here
        }
        for question in player_questions
    ]

    # Step 3: Insert questions individually into player_questions_collection
    player_questions_collection.insert_many(questions_for_session)
    print(f"20 questions for player_id {player_id} added to 'player_questions' collection.")



#THIS IS THE ORIGINAL!!!!!
# def fetch_random_questions(age, selected_topics):
#     age_group = get_age_group(age)
#     questions = list(questions_collection.find({"Age_Group": age_group, "topic": {"$in": selected_topics}}))
#
#     print("Fetched Questions:")
#     for q in questions:
#         print(q)
#
#     return sample(questions, min(len(questions), 20))


# Fetch and store 20 questions for a player in MongoDB
# THIS IS THE RIGHT ONE!!!!
     # age_group = get_age_group(age)
     # questions = list(questions_collection.find({"age_group":age_group,"topic":{"$in":selected_topics}}))
     # return sample(questions, min(len(questions),20))







#     try:
#         # Clear any existing questions for the player
#         mongo_collection.delete_many({"player_id": player_id})
#         # Call the new PostgreSQL function to fetch 20 random questions
#         pg_cursor.execute("SELECT * FROM get_random_questions();")
#         questions = pg_cursor.fetchall()
#
#         # Store questions in MongoDB
#         questions_to_store = [
#             {
#                 "player_id": player_id,
#                 "question_id": question['question_id'],
#                 "question_text": question['question_text'],
#                 "answer_a": question['answer_a'],
#                 "answer_b": question['answer_b'],
#                 "answer_c": question['answer_c'],
#                 "answer_d": question['answer_d'],
#                 "correct_answer": question['correct_answer'],
#             }
#             for question in questions
#         ]
#         mongo_collection.insert_many(questions_to_store)
#         print(f"Questions stored in MongoDB for player_id: {player_id}")
#     except Exception as e:
#         print("An error occurred while fetching and storing questions:", e)


def verify_player (username,password):
    """Verify if a returning player exists in PostgreSQL with an unfinished game."""
    try:
        pg_cursor.execute("SELECT player_id, password FROM players WHERE username = %s", (username,))
        result = pg_cursor.fetchone()
        if result and bcrypt.checkpw(password.encode(), result['password'].encode()):
            player_id = result['player_id']
            # Check if the game is unfinished by counting answers
            pg_cursor.execute("SELECT COUNT(*) FROM player_answers WHERE player_id = %s", (player_id,))
            questions_answered = pg_cursor.fetchone()[0]
            unfinished_game = questions_answered < 20
            return player_id, unfinished_game
    except Exception as e:
        print("Error verifying player:", e)
        return None, False

def fetch_remaining_questions(player_id):
    """Fetch the remaining questions for a returning player from player_questions_collection."""
    return list(player_questions_collection.find({"player_id": player_id, "is_answered": False}))


#That's ChatGPT's! the lines

def update_player_answer(player_id, question_no, selected_answer):
    """Checks the answer in player_questions_collection and sends the result to PostgreSQL."""
    question = player_questions_collection.find_one({"Question_No": question_no, "player_id": player_id})
    if question is None:
        print(f"No question found with Question_No {question_no} for player {player_id}")
        return

    correct_answer = question['Correct_Answer']
    is_correct = (selected_answer == correct_answer)
    try:
        query = "CALL update_player_answers (%s, %s, %s, %s)"
        pg_cursor.execute(query, (player_id, question_no, selected_answer, is_correct))
        connection.commit()

        # Update is_answered in MongoDB
        player_questions_collection.update_one(
            {"Question_No": question_no, "player_id": player_id},
            {"$set": {"is_answered": True}}
        )
    except Exception as e:
        print(f"An error occurred while updating player answers: {e}")
        connection.rollback()


# THAT'S THE ORIGINAL!!!!!
# def update_player_answer (player_id,question_id,selected_answer):
#     """Checks the answer in MongoDB and sends the data to PostgreSQL"""
#     question = questions_collection.find_one({"question_id":question_id})
#     correct_answer = question['Correct_Answer']
#     is_correct = (selected_answer == correct_answer)
#     try:
#         query = "CALL update_player_answers (%s,%s,%s,%s)"
#         pg_cursor.execute(query,(player_id,question_id,selected_answer,is_correct))
#         connection.commit()
#     except Exception as e:
#         print(f"An Error occurred while updating player answers: {e}")
#         connection.rollback()

def choose_topics(age):
    """Lets the user choose 3 topics to be asked about, according to his age"""
    age_topics = {
        (1,5): ["Animals", "Colours", "Food and Drinks", "Games", "Weather"],
        (5,10): ["Animals", "Math and Numbers", "Games", "Science", "Food and Drinks", "Anatomy", "Music", "Geography", "History", "Movies and TV Shows", "Nature", "Weather"],
        (10,15): ["Science", "Geography", "History", "Music", "Movies and TV Shows", "Literature and Books", "Health and Fitness", "Technology", "Arts and Crafts"],
        (15,20): ["Pop Culture", "Politics", "Travel", "Science", "History", "Health and Fitness", "Sports", "Technology", "Social Issues"],
        (20,30): ["Politics", "Technology", "Current Events", "Finance and Economics", "Health", "Arts and Culture", "Music", "Movies and TV Shows", "Travel and Landmarks"],
        (30,40): ["Family and Relationships", "Career and Work-Life Balance", "Home and Lifestyle", "Health and Fitness", "Travel", "Finance and Economics"],
        (40,100): ["History", "Health and Wellness", "Culture and Arts", "Travel", "Current Events"]
    }
    topics = next(value for key, value in age_topics.items() if key[0] <= age <key[1])
    print("Please Choose 3 of the following topics:")
    for idx, topic in enumerate(topics, start=1):
        print(f"\033[95m{idx}. {topic}{' ':<50}\033[96m")
    selected_topics = []
    while len(selected_topics) < 3:
        choice = input(f"\033[94mEnter Your Topics (You can either choose by topic or by number):").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(topics):
            topic = topics[int(choice)-1]
            # if topic and topic not in selected_topics:
            #     selected_topics.append(topic)
        else:
            topic = next((t for t in topics if t.lower() == choice.lower()),None)
        if topic and topic not in selected_topics:
            selected_topics.append(topic)
        else:
            print("Invalid Choice... Please try again")
        if choice in topics and choice not in selected_topics:
            selected_topics.append(choice)
    print(f"OK, You've selected the following topics:\n{selected_topics}")
    return selected_topics


def start_quiz(player_id):
    """Starts the quiz using questions from the player's questions set in player_questions_collection"""
    questions = list(player_questions_collection.find({"player_id":player_id}))

    if not questions:
        print("No questions available for the selected topics and age group.")
        return main_menu()  # Exit or prompt to select again

    for i, color in zip(range(5), itertools.cycle(colors)):
        text = f"{color}GET READY, STARTING THE QUIZ!{reset}"
        print(f"\r{' '}\r{text.center(140)}", end="", flush=True)
        time.sleep(2)
    update_starting_time(player_id)
    question_counter = 0
    while questions:
        question = questions.pop(0)  # Pop the first question from the list
        question_id = question.get('Question_No')  # Use 'Question_No' as the unique identifier


        print(f"Current question ID: {question_id}")  # Debugging statement

        if not question:
            print("You've answered all the questions! Well done!")
            complete_game(player_id)
            #query = "CALL update_high_score_table_finish_time(%s);"
            #pg_cursor.execute(query, (player_id,))
            #connection.commit()
            sleep(2)
            return main_menu()
        question_counter += 1
        print(f"{' ':<35}{question_counter}. {question['Question_Text']}\033[0m\n")
        sleep(2)
        print(f"\033[95m{' ':<40}{'a.'}{question['Answer_a']:<40}\033[0m", end='')  # Answer a starts after 40 spaces
        sleep(1)
        print(f"\033[92m{' b.' + question['Answer_b']}\033[0m\n")
        sleep(1)
        print(f"\033[93m{' ':<40}{'c.'} {question['Answer_c']:<40}\033[0m", end='')
        sleep(1)
        print(f"\033[94m{'d.' + question['Answer_d']}\033[0m\n")
        sleep(1)

        selected_answer = check_to_quit(input(
            f"Please enter your answer:\nIs it \033[95m(a)\033[0m, \033[92m(b)\033[0m, \033[93m(c)\033[0m, or \033[94m(d)\033[0m? \n\033[96mRemember you can hit [Q] at any time to quit!\033[0m\n").lower(),
                                        player_id)

        if not selected_answer == 'q':
            update_player_answer(player_id, question_id, selected_answer)

            # Delete the question in MongoDB
            # delete = questions_collection.delete_one({"Question_No": question_id})
            # print(f"Attempting to delete question with Question_No {question_id}") #### to be deleted later?

            # if delete.deleted_count == 1:
            #     print(f"Question with Question_No {question_id} deleted successfully.")
            # else:
            #     print(f"Failed to delete question with Question_No {question_id}.")

            if selected_answer == question['Correct_Answer']:
                print("Correct Answer!")
            else:
                print(f"Wrong Answer... Too Bad...\nThe Correct Answer was: {question['Correct_Answer']}.")
        else:
            break

    print("You've answered all the questions! Well done!")
    complete_game(player_id)
    #query = "CALL update_high_score_table_finish_time(%s);"
    #pg_cursor.execute(query, (player_id,))
    #connection.commit()
    return main_menu()

    # Proceed with the quiz logic here

# def start_quiz(player_id, questions):
#     print("Starting quiz with questions:", questions)  # Debugging line
#     if not questions:
#         print("No questions found for the selected age group and topics.")
#         return main_menu()
#     # Rest of your start_quiz logic

#THATS THE ORIGINAL!!!!!!
# def start_quiz(player_id, questions):
#     """Starts the quiz for a player and deletes each question after it's answered"""
#     for i, color in zip(range(5), itertools.cycle(colors)):
#         text = f"{color}GET READY, STARTING THE QUIZ!{reset}"
#         print(f"\r{' '}\r{text.center(140)}", end="", flush=True)
#         time.sleep(2)
#     while True:
#         question = questions.pop(0)
#         question_id = question['question_id']
#
#         if not question:
#             print("You've answered all the questions! Well done!")
#             query = "CALL update_high_score_table_finish_time(%s);"
#             pg_cursor.execute(query, (player_id,))
#             connection.commit()
#             return main_menu()
#         else:
#             for question in questions:
#                 print("\n")
#                 print(f"{' ':<50}{question['question_text']}\033[0m\n")  # Reset color to white for the question text
#                 sleep(2)
#                 print(f"\033[95m{' ':<40}{'a.'}{question['answer_a']:<40}\033[0m", end='')  # Answer a starts after 40 spaces
#                 sleep(1)
#                 print(f"\033[92m{' b.' + question['answer_b']}\033[0m\n")  # Answer b starts after 60 spaces
#                 sleep(1)
#                 print(f"\033[93m{' ':<40}{'c.'} {question['answer_c']:<40}\033[0m", end='')  # Answer c starts after 40 spaces
#                 sleep(1)
#                 print(f"\033[94m{'d.' + question['answer_d']}\033[0m\n")
#                 (sleep(1))
#                 selected_answer = check_to_quit(input(
#                     f"Please enter your answer:\nIs it \033[95m(a)\033[0m, \033[92m(b)\033[0m, \033[93m(c)\033[0m, or \033[94m(d)\033[0m? \n\033[96mRemember you can hit [Q] at any time to quit!\033[0m\n").lower(), player_id)
#                 if not selected_answer == 'q':
#                     update_player_answer(player_id, question_id, selected_answer)
#                     delete = questions_collection.delete_one({"_id": question['_id']})
#                     # Call this function after each answer is processed and the question is deleted
#                     print_remaining_questions(player_id)
#
#                     if delete.deleted_count == 1:
#                         print(f"Question {question['_id']} deleted successfully.")
#                     else:
#                         print(f"Failed to delete question {question['_id']}.")
#
#                     if selected_answer == question['correct_answer']:
#                         print("Correct Answer!")
#                     else:
#                         print(f"Wrong Answer... Too Bad...\nThe Correct Answer was: {question['correct_answer']}.")
#                 else:
#                     break
#             print("You've answered all the questions! Well done!")
#             query = "CALL update_high_score_table_finish_time(%s);"
#             pg_cursor.execute(query,(player_id,))
#             connection.commit()
#             return main_menu()

def update_starting_time (player_id):
    """Updates the quiz's starting time at the high_scores table"""
    query = "CALL update_high_score_table_start_time(%s)"
    pg_cursor.execute(query,(player_id,))
    connection.commit()




    # Check and process new entries from new_player_log
    # while True:
    #     pg_cursor.execute("SELECT * FROM new_player_log;")
    #     new_entries = pg_cursor.fetchall()
    #
    #     for entry in new_entries:
    #         player_id = entry['player_id']
    #         fetch_and_store_questions(player_id, pg_cursor, player_questions_collection)
    #         pg_cursor.execute("DELETE FROM new_player_log WHERE player_id = %s;", (player_id,))
    #         connection.commit()


# finally:
#     # Close PostgreSQL connection
#     if pg_cursor:
#         pg_cursor.close()
#     if connection:
#         connection.close()
#     print("t")
#     # Fetch and print all documents in MongoDB collection
#     questions = player_questions_collection.find()
#     for question in questions:
#         print(question)
#
#     # Close MongoDB connection
#     if mongo_client:
#         mongo_client.close()



# Function to check a password
# def check_password(username, password,email,age):
#     # Retrieve the hashed password from the database
#     pg_cursor.execute("SELECT hashed_password FROM users WHERE username = %s", (username,))
#     result = pg_cursor.fetchone()
#
#     if result:
#         hashed_password_from_db = result[0]dont forget it worked before, only that i found out the correct answers
#         # Compare the provided password with the stored hash
#         if bcrypt.checkpw(password.encode(), hashed_password_from_db.encode()):
#             print("Password is correct!")
#         else:
#             print("Incorrect password!")
#     else:
#         print("Username not found.")
#
#
# # Example usage
#   # Creating a new user
# check_password('user1', 'my_password1')  # Verifying the password
#
# # Close connection
# pg_cursor.close()
# connection.close()
def print_statistics_table(results):
    """Shows a general statistics table"""
    headers = ["Player ID", "Username", "Questions Solved", "Started At", "Finished At", "Total Game Time", "Score"]

    print(f"\n\n| {' | '.join(f'{header:^20}' for header in headers)} | ")
    print("|" + "|".join("-" * 22 for _ in headers) + "|")

    for row in results:
        started_at = f"{row['started_at']:%Y-%m-%d %H:%M:%S}" if row.get('started_at') else "N/A"
        finished_at = f"{row['finished_at']:%Y-%m-%d %H:%M:%S}" if row.get('finished_at') else "N/A"
        total_game_time = str(row['total_game_time']).split('.')[0] if row.get('total_game_time') else "N/A"

        print(f"| {row['player_id']:^20} | {row['username']:^20} | {row['questions_solved']:^20} | "
              f"{started_at:^20} | {finished_at:^20} | {total_game_time:^20} | {row['score']:^20} |")
    print(f"\n\n")
    sleep(2)
    main_menu()



def print_past_players_table(results):
    """Prints a table showing all past players."""
    headers = ["Player ID", "Username", "Age", "E-mail", "Registration Date", "Total Players"]

    # Print headers
    print(f"\n\n| {' | '.join(f'{header:^20}' for header in headers)} | ")
    print("|" + "|".join("-" * 22 for _ in headers) + "|")

    # Loop through each player row
    for row in results:
        # Format the fields correctly
        player_id = row.get('player_id', 'N/A')
        username = row.get('username', 'N/A')
        age = row.get('age', 'N/A')
        email = row.get('email', 'N/A')
        registration_date = (
            row.get('registration_date').strftime("%Y-%m-%d")
            if isinstance(row.get('registration_date'), datetime)
            else "N/A"
        )
        total_players = row.get('total_players', 'N/A')

        # Print row data
        print(f"| {player_id:^20} | {username:^20} | {age:^20} | {email:^20} | {registration_date:^20} | {total_players:^20} |")
    print("\n\n")
    sleep(2)
    main_menu()




#THIS WAS GIVEN BY CHATGPT!


def print_questions_statistics_table():
    """Retrieves data from PostgreSQL and MongoDB, printing tables for most and least answered questions with colors by age group."""

    headers = ["Age", "Topic", "Q.ID", "Question Text", "Correct", "Incorrect", "Total"]
    column_widths = [6, 30, 6, 120, 8, 10, 8]

    # ANSI color codes for different age groups
    colors = {
        "1-5": "\033[92m",       # Bright Green
        "5-10": "\033[34m",      # Blue
        "10-15": "\033[95m",     # Purple
        "15-20": "\033[93m",     # Bright Yellow
        "20-30": "\033[96m",     # Bright Cyan
        "30-40": "\033[91m",     # Red
        "40-100": "\033[94m",    # Bright Blue
    }
    reset_color = "\033[0m"  # Reset to default

    # Fetch data from PostgreSQL
    pg_cursor.execute("SELECT * FROM most_least_answered_questions()")
    results = pg_cursor.fetchall()

    # Print headers in white
    print("\033[97m\nMost Answered Questions:")  # White
    header_row = "| " + " | ".join(f"{header:^{column_widths[i]}}" for i, header in enumerate(headers)) + " |"
    separator_row = "|" + "|".join("-" * (width + 2) for width in column_widths) + "|"
    print(header_row)
    print(separator_row)
    print(reset_color, end="")  # Reset color after headers

    for row in results:
        question_id, total_answered_times, total_correct_times, total_incorrect_times = row[:4]

        # Fetch question details from MongoDB
        question_doc = questions_collection.find_one({"Question_No": question_id})
        question_text = question_doc.get("Question_Text", "N/A")
        age_group = question_doc.get("Age_Group", "N/A")
        topic = question_doc.get("Topic", "N/A")

        # Determine the color based on age group
        color_code = colors.get(age_group, "\033[0m")  # Default to no color if age group not in colors

        # Print the row with the determined color
        print(color_code + f"| {age_group:^{column_widths[0]}} | {topic:^{column_widths[1]}} | {question_id:^{column_widths[2]}} | "
              f"{question_text[:column_widths[3]]:{column_widths[3]}} | {total_correct_times:^{column_widths[4]}} | "
              f"{total_incorrect_times:^{column_widths[5]}} | {total_answered_times:^{column_widths[6]}} |" + reset_color)

    print("\n")  # Final newline for spacing
    sleep(2)
    main_menu()



#### 1-5 and their data in green, ages 5-10 and their data in blue, ages 10-15 and their data in purple, ages 15-20 and their data in yellow, ages 20-30 and their data in orenge, ages 30-40 and their data in red and ages 40-100 and their data in pink.


#THIS IS THE ORIGINAL!!!!
# def print_questions_statistics_table():
#     """Retrieves data from postgres and MongoDB and prints a table of most and least answered questions."""
#     # Fetch data from PostgreSQL for most/least answered questions
#     pg_cursor.execute("SELECT * FROM most_least_answered_questions()")
#     results = pg_cursor.fetchall()
#     print(results)
#     most_answered_list = list(questions_collection.aggregate([
#         {"$match": {
#             "question_text": {"$ne": None},
#             "Question_No": {"$ne": None}
#         }},
#         {"$group": {
#             "_id": {"age_group": "$Age_Group", "topic": "$Topic"},
#             "question": {"$first": "$Question_Text"},
#             "question_id": {"$first": "$Question_No"},
#             "total_answered_times": {"$max": "$answered_count"}
#         }},
#         {"$sort": {"total_answered_times": -1}}
#     ]))
#
#     least_answered_list = list(questions_collection.aggregate([
#         {"$match": {
#             "question_text": {"$ne": None},
#             "Question_No": {"$ne": None}
#         }},
#         {"$group": {
#             "_id": {"age_group": "$Age_Group", "topic": "$Topic"},
#             "question": {"$first": "$Question_Text"},
#             "question_id": {"$first": "$Question_No"},
#             "total_answered_times": {"$min": "$answered_count"}
#         }},
#         {"$sort": {"total_answered_times": 1}}
#     ]))
#     headers_most_answered = ["Age Group", "Topic", "Question ID", "Question Text", "Username", "Player's Age", "Date Answered", "Total Answered Times"]
#     print("\nMost answered questions:")
#     print(f"\n\n| {' | '.join(f'{header:^20}' for header in headers_most_answered)} | ")
#     print("|" + "|".join("-" * 22 for _ in headers_most_answered) + "|")
#     for doc in most_answered_list:
#         age_group = doc["_id"]["age_group"]
#         topic = doc["_id"]["topic"]
#         question_id = results[0]
#         question = doc["question"]
#         username = doc["username"]
#         player_age = doc["age"]
#
#         total_answered_times = results[1]
#         total_correct_times = results[2]
#         total_incorrect_times = results[3]
#
#         print(f"| {age_group:^20} | {topic ^ 20} | {question_id:^20} | {question_text} | {username} | {player_age} | {date_answered} | {total_answered_times:^20}")
#
#     headers_least_answered = ["Age Group", "Topic", "Question ID", "Question Text", "Username", "Player's Age", "Date Answered", "Total Answered Times"]
#     print("\nLeast answered questions:")
#     print(f"\n\n| {' | '.join(f'{header:^20}' for header in headers_least_answered)} | ")
#     print("|" + "|".join("-" * 22 for _ in headers_least_answered) + "|")
#     for doc in least_answered_list:
#         age_group = doc["_id"]["age_group"]
#         topic = doc["_id"]["topic"]
#         question = doc["question"]
#         question_id = results[0]
#         total_answered_times = results[1]
#         total_correct_times = results[2]
#         total_incorrect_times = results[3]
#
#         print(f"| {age_group:^20} | {topic ^ 20} | {question_id:^20} | {question_text} | {username} | {player_age} | {date_answered} | {total_answered_times:^20}")
#     sleep(2)
#     main_menu()





    # most_answered_list = list(most_answered_questions)
    # least_answered_list = list(least_answered_questions)



    #
    # print("\nLeast Answered Questions:")
    # for doc in least_answered_list:
    #     print(doc)






    # for row in headers_most_answered:
    #     registration_date = f"{row['registration_date']:%Y-%m-%d}" if row['registration_date'] else "N/A"
    #     print(f"| {row['player_id']:^20} | {row['username']:^20} | {row['age']:^20} | "
    #           f"{row['email']:^20} | {registration_date:^20} | {row['total_players']:^20} |")
    # print(f"\n\n")






    # for row in headers_least_answered:
    #     registration_date = f"{row['registration_date']:%Y-%m-%d}" if row['registration_date'] else "N/A"
    #     print(f"| {row['player_id']:^20} | {row['username']:^20} | {row['age']:^20} | "
    #           f"{row['email']:^20} | {registration_date:^20} | {row['total_players']:^20} |")
    # print(f"\n\n")


def get_user_statistics(player_id):
    """Retrieves and shows the user's personal statistics from all games in the 'high_score' table"""
    pg_cursor.execute("SELECT * FROM show_user_statistics(%s);", (player_id,))
    connection.commit()
    results = pg_cursor.fetchall()
    print_statistics_table(results)
    sleep(5)
    return main_menu()



def get_user_best_score(player_id):
    """Retrieves and shows the user's personal best from all games"""
    pg_cursor.execute("SELECT * FROM show_user_best_score(%s);", (player_id,))
    result = pg_cursor.fetchone()  # Fetches only one row

    if result:
        print_statistics_table([result])  # Pass a list containing the single row to match expected format
    else:
        print("No best score found for this player.")
    sleep(5)
    return main_menu()





def show_high_score_table():
    """Shows the 'high_score' table"""
    pg_cursor.execute("SELECT * FROM show_high_score_table();")
    connection.commit()
    results = pg_cursor.fetchall()
    print_statistics_table(results)



def past_players():
    """Retrieves data from postgres and sends it to be printed as a table of past players"""
    pg_cursor.execute("SELECT * FROM past_players_list();")
    connection.commit()
    results = pg_cursor.fetchall()
    print(results)
    print_past_players_table(results)

    sleep(5)
    return main_menu()

# def questions_statistics():
#     """Retrieves data from postgres and sends it to be printed as a table of most and least answered questions"""
#     # pg_cursor.execute("SELECT * FROM questions_statistics();")
#     # connection.commit()
#     # results = pg_cursor.fetchall()
#     print_questions_statistics_table()

def check_to_quit(user_input, player_id = None):
    if user_input == 'q':
        if player_id:
            quit_game(player_id)

        return main_menu()
    return user_input

def get_age_group(age):
    """Determine the age group range for a given age"""

    age_groups = {
        "1-5": range(1,6),
        "5-10": range(6,11),
        "10-15": range(11,16),
        "15-20": range(16,21),
        "20-30": range(21,31),
        "30-40": range(31,41),
        "40-100": range(41,101)
    }
    for group, age_range in age_groups.items():
        if age in age_range:
            return group
        elif 0 >= age > 100:
            print("No matching age groups for this age")

def quit_game (player_id):
    pg_cursor.execute("CALL update_session_time(%s);", (player_id,))
    connection.commit()
    print("Game session saved. You can resume later at any time")

def complete_game(player_id):
    pg_cursor.execute("CALL update_high_score_table_when_quiz_finished(%s);", (player_id,))
    connection.commit()
    print("Congratulations! Game completed!")
def main_menu():
    print("Hello, and welcome to:".center(130, " "))  # Manually set the center width to 120
    time.sleep(2)

    # Limit to 10 cycles, for example
    for i, color in zip(range(5), itertools.cycle(colors)):
        text = f"{color}The Trivia Game!{reset}"
        print(f"\r{' '}\r{text.center(140)}", end="", flush=True)
        time.sleep(2)
    print("\n")  # Ensure the last line doesn't get overwritten


    action = input("Please choose one of the options below:\n\n\
    1. New Player Sign-in [Press N]\n\
    2. Existing Player Log-in [Press E]\n\
    3. Show Statistics [Press S]\n\
    4. Quit the Game [Press Q]\n\n").lower()
    match action:
        case 'n' | '1':
            while True:
                username = check_to_quit(input("Please enter a username: \n"))
                password = check_to_quit(input("Please enter a password: \n"))
                reenter_password = check_to_quit(input("Please re-enter your Password: \n"))
                email = check_to_quit(input("Please enter your E-mail address: \n"))
                age= check_to_quit(int(input("Please enter your age: \n")))
                get_age_group(age)
                if password != reenter_password:
                    again_or_quit = input("Passwords mismatch. Please try again or press [q] to go back to main menu")
                    if again_or_quit == 'q':
                        return main_menu()
                    else:
                        continue
                if password == reenter_password:
                    player_id = insert_new_player(username, password, email, age)
                    if player_id:
                        print(f"Player {username} created successfully with ID:\n{player_id} ")
                        selected_topics = choose_topics(age)
                        create_player_questions_set(player_id,get_age_group(age),selected_topics)
                        start_quiz(player_id)

                    else:
                        print("Failed to create player. Please try again.")
                        return main_menu()
                # else:
                #     print("Passwords do not match. Please try again.")
                #     main_menu()
        case 'e' | '2':
            username = check_to_quit(input("Please enter a username: \n"))
            password = check_to_quit(input("Please enter a password: \n"))
            player_id, unfinished_game = verify_player(username,password)
            if player_id:
                print(f"Welcome back, {username}!")
                if unfinished_game:
                    questions = fetch_remaining_questions(player_id)
                    start_quiz(player_id)
                else:
                    complete_game(player_id)
                    print("It looks like you've completed the quiz. Bravo!")
                    time.sleep(2)
                    main_menu()
            else:
                print("Invalid login or finished game. Please try again")
        case 's' | '3':
            user_input = input(f"Would you like to:\n1. See Your overall Statistics\n2. See Your best performance yet\
            \n3. See all time best scores\n4. See number of players so far\n5. See details for most and least answered questions\n10. Quit ")
            if user_input == '1':
                username = check_to_quit(input("Please enter a username: \n"))
                password = check_to_quit(input("Please enter a password: \n"))
                player_id = verify_player(username, password)
                get_user_statistics(player_id[0])
            elif user_input == '2':
                username = check_to_quit(input("Please enter a username: \n"))
                password = check_to_quit(input("Please enter a password: \n"))
                player_id = verify_player(username, password)
                get_user_best_score(player_id[0])
            elif user_input == '3':
                show_high_score_table()
            elif user_input == '4':
                past_players()
            elif user_input == '5':
                print_questions_statistics_table()
            elif user_input == '10' or user_input == 'q':
                user_input= 'q'
                check_to_quit(user_input)
        case 'q' | '4':
            print("Sorry to see you leave. Goodbye.")
            exit()


# def print_remaining_questions(player_id):
#     """Prints remaining questions for a player's current game session from player_questions_collection."""
#     remaining_questions = player_questions_collection.find({"player_id": player_id})
#     print("\nRemaining questions:")
#     for question in remaining_questions:
#         print(f"Question: {question['Question_Text']}, Correct Answer: {question['Correct_Answer']}")







main_menu()

