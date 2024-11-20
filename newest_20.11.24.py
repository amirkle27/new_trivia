#
#
# # pip install matplotlib !!!
#


import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
##############################################
import time
import itertools
from datetime import datetime
from time import sleep
import psycopg2
import psycopg2.extras
from numpy.f2py.auxfuncs import ischaracter
from pymongo import MongoClient
import bcrypt
from random import sample


connection = psycopg2.connect(
        host="localhost",
        database="postgres",
        user="postgres",
        password="admin",
        port="5432"
    )
pg_cursor = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
client = MongoClient("mongodb://localhost:27017/")
mongo_db = client["Trivia_MongoDB"]
questions_collection = mongo_db["questions"]
player_questions_collection = mongo_db['player_questions']

colors = [
        "\033[91m",  # Red
        "\033[92m",  # Green
        "\033[33m",  # Yellow
        "\033[94m",  # Blue
        "\033[95m",  # Magenta
        "\033[96m",  # Cyan
    ]
reset = "\033[0m"  # Reset color to default


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
import plotly.express as px
#
# def plot_answer_distribution_interactive(correct, wrong, unanswered):
#     labels = ['Correct', 'Wrong', 'Not Answered']
#     sizes = [correct, wrong, unanswered]
#
#     fig = px.pie(values=sizes, names=labels, title="Answer Distribution")
#     fig.show()
#
# # Example usage:
# plot_answer_distribution_interactive(25, 10, 5)
#
#
# def plot_answer_distribution(correct, wrong, unanswered):
#     labels = ['Correct', 'Wrong', 'Not Answered']
#     sizes = [correct, wrong, unanswered]
#     colors = ['yellowgreen', 'red', 'gold']
#     explode = (0.1, 0, 0)  # To "explode" the first slice
#
#     plt.figure(figsize=(8, 8))
#     plt.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%',
#             shadow=True, startangle=90)
#     plt.axis('equal')  # Equal aspect ratio ensures the pie chart is a circle
#     plt.title("Answer Distribution")
#     plt.show()
#
# # Example usage:
# plot_answer_distribution(correct=25, wrong=10, unanswered=5)
#
# def plot_topic_popularity(topics, counts):
#     percentages = [count / sum(counts) * 100 for count in counts]
#
#     plt.figure(figsize=(10, 6))
#     plt.bar(topics, percentages, color='skyblue')
#     plt.xlabel("Topics")
#     plt.ylabel("Percentage of Players (%)")
#     plt.title("Popularity of Topics Chosen by Players")
#     plt.xticks(rotation=45, ha='right')  # Rotate for readability
#     plt.tight_layout()
#     plt.show()
#
# # Example usage:
# topics = ['Science', 'History', 'Music', 'Sports']
# counts = [30, 25, 45, 20]
# plot_topic_popularity(topics, counts)
#
# def plot_performance_trend(game_ids, scores):
#     plt.figure(figsize=(10, 6))
#     plt.plot(game_ids, scores, marker='o', color='blue')
#     plt.xlabel("Game ID")
#     plt.ylabel("Score")
#     plt.title("Player's Performance Over Time")
#     plt.grid()
#     plt.show()
#
# # Example usage:
# game_ids = [1, 2, 3, 4, 5]
# scores = [50, 65, 70, 60, 80]
# plot_performance_trend(game_ids, scores)
#
#
# def plot_age_topic_heatmap(age_groups, topics, engagement):
#     plt.figure(figsize=(10, 8))
#     sns.heatmap(engagement, annot=True, fmt="d", cmap="YlGnBu",
#                 xticklabels=topics, yticklabels=age_groups)
#     plt.xlabel("Topics")
#     plt.ylabel("Age Groups")
#     plt.title("Age Group vs. Topic Engagement")
#     plt.show()
#
# # Example usage:
# age_groups = ['1-5', '5-10', '10-15', '15-20']
# topics = ['Science', 'History', 'Music', 'Sports']
# engagement = np.array([[5, 3, 8, 2], [7, 6, 10, 3], [9, 8, 12, 6], [4, 5, 9, 7]])
# plot_age_topic_heatmap(age_groups, topics, engagement)


def print_table(data, headers, column_widths,row_colors=None):
    """Dynamically prints a table with specified headers, data, and column widths."""
    # Ensure the headers align with the column widths
    header_row = "| " + " | ".join(f"{header:^{column_widths[i]}}" for i, header in enumerate(headers)) + " |"
    separator_row = "|" + "|".join("-" * (width + 2) for width in column_widths) + "|"
    print("\033[97m" + header_row + "\033[0m")  # White for headers
    print(separator_row)

    # Identify the column(s) to left-align based on headers
    left_align_columns = {i for i, header in enumerate(headers) if "Question Text" in header or "Topic" in header}

    # Print rows with dynamic alignment and optional row colors
    for idx, row in enumerate(data):
        color = row_colors[idx] if row_colors and idx < len(row_colors) else "\033[0m"  # Default to no color
        row_text = "| " + " | ".join(
            f"{str(row[i]):<{column_widths[i]}}" if i in left_align_columns else f"{str(row[i]):^{column_widths[i]}}"
            for i in range(len(headers))
        ) + " |"
        print(color + row_text + "\033[0m")  # Reset color after each row
    print("\n")  # Newline for spacing

def format_results(results, keys, default="N/A"):
    """
    Formats a list of dictionaries (`results`) into a list of lists based on the provided keys.
    - results: List of dictionaries containing the data.
    - keys: List of keys to extract from each dictionary.
    - default: Default value to use if a key is missing.
    """
    return [
        [row.get(key, default) for key in keys]
        for row in results
    ]
def present_statistics_menu():
    """Presents the statistics menu"""
    user_input = input(f"Would you like to:\n1. See Your overall Statistics\n2. See Your best performance yet\
                \n3. See a player's last game's statistics\n4. Get a full list of questions a player has been asked\n5. See a list of correct answers given by a user (by user id)\
                \n6. Check for all time correct answers\n7. See all time best scores\n8. See number of players so far\n9. See details for most and least answered questions\n10. Quit ")
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
        username = check_to_quit(input("Please enter a username: \n"))
        password = check_to_quit(input("Please enter a password: \n"))
        player_id = verify_player(username, password)
        if player_id:
            get_mid_game_statistics(player_id[0])
            sleep(5)
            main_menu()
    elif user_input == '4':
        username = check_to_quit(input("Please enter a username: \n"))
        password = check_to_quit(input("Please enter a password: \n"))
        player_id = verify_player(username, password)
        if player_id:
            user_answers(player_id[0])
        else:
            print("No player found with the provided ID")
            main_menu()
    elif user_input == '5':
        username = check_to_quit(input("Please enter a username: \n"))
        password = check_to_quit(input("Please enter a password: \n"))
        player_id = verify_player(username, password)
        if player_id:
            user_correct_answers(player_id[0])
        else:
            print("No player found with the provided ID")
            main_menu()
    elif user_input == '6':
        answered_correctly_count_list()
    elif user_input == '7':
        show_high_score_table()
    elif user_input == '8':
        past_players()
    elif user_input == '9':
        most_least_answered_questions_table()
    elif user_input == '10' or user_input == 'q':
        user_input = 'q'
        check_to_quit(user_input)

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

def verify_player (username,password):
    """Verify if a returning player exists in PostgreSQL with an unfinished game."""
    try:
        pg_cursor.execute("SELECT player_id, password, age FROM players WHERE username = %s", (username,))
        result = pg_cursor.fetchone()
        if result and bcrypt.checkpw(password.encode(), result['password'].encode()):
            player_id = result['player_id']
            age = result['age']
            # Check unfinished game in MongoDB
            remaining_questions = player_questions_collection.count_documents(
                {"player_id": player_id, "is_answered": False})
            unfinished_game = remaining_questions > 0
            return player_id,unfinished_game,age
        else:
            return None,False,None
    except Exception as e:
        print("Error verifying player:", e)
        return None, False, None

    #         # Check if the game is unfinished by counting answers
    #         pg_cursor.execute("SELECT COUNT(*) FROM player_answers WHERE player_id = %s", (player_id,))
    #         questions_answered = pg_cursor.fetchone()[0]
    #         unfinished_game = questions_answered < 20
    #         return player_id, unfinished_game, age
    #     else:
    #         return None, False, None
    # except Exception as e:
    #     print("Error verifying player:", e)
    #     return None, False, None

def fetch_remaining_questions(player_id):
    """Fetch the remaining questions for a returning player from player_questions_collection."""
    return list(player_questions_collection.find({"player_id": player_id, "is_answered": False}))

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

def choose_topics(age):
    """Lets the user choose 3 topics to be asked about, according to his age"""
    age_topics = {
        (1,5): ["Animals", "Colours", "Food and Drinks", "Games", "Weather"],
        (5,10): ["Animals", "Math and Numbers", "Games", "Science", "Food and Drinks", "Anatomy", "Music", "Geography", "History", "Movies and TV Shows", "Nature", "Weather"],
        (10,15): ["Science", "Geography", "History", "Music", "Movies and TV Shows", "Literature and Books", "Health and Fitness", "Technology", "Arts and Crafts"],
        (15,20): ["Pop Culture", "Politics", "Travel", "Science", "History", "Health and Fitness", "Sports", "Technology", "Social Issues"],
        (20,30): ["Politics", "Technology", "Current Events", "Finance and Economics", "Health", "Arts and Culture", "Music", "Movies and TV Shows", "Travel and Landmarks"],
        (30,40): ["Family and Relationships", "Career and Work-Life Balance", "Home and Lifestyle", "Health and Fitness", "Travel", "Finance and Economics"],
        (40,101): ["History", "Health and Wellness", "Culture and Arts", "Travel", "Current Events"]
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

def question_structure(question_counter,question):
    """prints a question and 4 possible answers in a structured form"""
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

def start_quiz(player_id, player_age):
    """Starts the quiz using questions from the player's questions set in player_questions_collection"""
    questions = fetch_remaining_questions(player_id)
    if not questions:
        print("No unfinished quiz found for this player. Starting a new game:")
        topics = choose_topics(player_age)
        create_player_questions_set(player_id, get_age_group(player_age), topics)
        update_starting_time(player_id)
        questions = fetch_remaining_questions(player_id)

    # if not questions:
    #     print("No questions available for the selected topics and age group.")
    #     return main_menu()  # Exit or prompt to select again

    for i, color in zip(range(5), itertools.cycle(colors)):
        text = f"{color}GET READY, STARTING THE QUIZ!{reset}"
        print(f"\r{' '}\r{text.center(140)}", end="", flush=True)
        time.sleep(2)
    update_starting_time(player_id)
    question_counter = player_questions_collection.count_documents(
        {"player_id": player_id, "is_answered": True}) + 1
    while questions:
        question = questions.pop(0)  # Pop the first question from the list
        question_id = question.get('Question_No')  # Use 'Question_No' as the unique identifier

        print(f"Current question ID: {question_id}")  # Debugging statement
        question_structure(question_counter, question)
        valid_answers = ['a', 'b', 'c', 'd', 's', 'q']
        if not question:
            print("You've answered all the questions! Well done!")
            complete_game(player_id)
            sleep(2)
            return main_menu()

        while True:
            selected_answer = check_to_quit(input(
                f"Please enter your answer:\nIs it \033[95m(a)\033[0m, \033[92m(b)\033[0m, \033[93m(c)\033[0m, or \033[94m(d)\033[0m? "
                f"\n\033[96mRemember you can hit [S] for statistics or [Q] to quit at any time!\033[0m\n").strip().lower(), player_id)
            while not selected_answer in valid_answers:
                selected_answer = check_to_quit(input(f"Invalid input. Please choose one of \033[95ma\033[0m, \033[92mb\033[0m, \033[93mc\033[0m, \033[94md\033[0m:"))


            # if selected_answer not in ['a','b','c','d']:
            #      print("Invalid input. Please enter 'a', 'b', 'c', or 'd'.")
            #      continue

            if selected_answer == 's':
                choice = input("Would you like to:\n1. See current game's statistics [Press 1 or C]\n2. See other statistics [Press 2 or O]").strip().lower()
                match choice:
                    case "1" | "c":
                            try:
                                print("\nFetching mid-game statistics...\n")
                                get_mid_game_statistics(player_id)
                            except Exception as e:
                                print(f"Error fetching statistics: {e}")
                            sleep(2)
                            question_structure(question_counter,question)
                            continue  # Return to the current question
                    case "2" | "o":
                        present_statistics_menu()
                # get_mid_game_statistics(player_id)
                # present_statistics_menu()
            elif selected_answer == 'q':
                quit_game(player_id)
                return main_menu()
            elif selected_answer == question['Correct_Answer']:
                print(f"\033[92mCorrect Answer!\033[0m")
                update_player_answer(player_id, question_id, selected_answer)
            else:
                print(f"\033[91mWrong Answer... Too Bad...\033[0m\n\033[94mThe Correct Answer was:\033[0m {question['Correct_Answer']}.")
                update_player_answer(player_id, question_id, selected_answer)
            if selected_answer in ['a', 'b', 'c', 'd']:
                question_counter +=1
                break

    print("You've answered all the questions! Well done!")
    complete_game(player_id, player_age)
    return main_menu()

def update_starting_time (player_id):
    """Updates the quiz's starting time at the high_scores table"""
    query = "CALL update_high_score_table_start_time(%s)"
    pg_cursor.execute(query,(player_id,))
    connection.commit()

#option 1:
def print_statistics_table(results):
    """Shows a general statistics table"""
    headers = ["Player ID", "Username", "Questions Solved", "Started At", "Finished At", "Total Game Time", "Score"]
    column_widths = [10, 20, 20, 20, 20, 20, 10]
    keys = ["player_id", "username", "questions_solved", "started_at", "finished_at", "total_game_time", "score"]

    # Format results using the new function
    formatted_results = format_results(results, keys)
    # Use the updated print_table function
    print_table(formatted_results, headers, column_widths)
    print("\n\n")
    sleep(5)
    main_menu()


# def print_past_players_table(results):
#     """Prints a table showing all past players."""
#     headers = ["Player ID", "Username", "Age", "Email", "Registration Date", "Total Players"]
#     column_widths = [10, 20, 10, 30, 26, 15]
#     keys = ["player_id", "username", "age", "email", "registration_date", "total_players"]
#
#     # Format results using the new function
#     formatted_results = format_results(results, keys)
#
#     print_table(formatted_results, headers, column_widths)
#     sleep(5)
#     main_menu()

#option 8:
def most_least_answered_questions_table():
    """Retrieves data from PostgreSQL and MongoDB, printing tables for most and least answered questions with colors by age group."""

    headers = ["Age Group", "Topic", "Question ID", "Question Text", "Correct", "Incorrect", "Total"]
    column_widths = [10, 30, 11, 120, 10, 10, 10]

    # Fetch data from PostgreSQL
    pg_cursor.execute("SELECT * FROM most_least_answered_questions()")
    results = pg_cursor.fetchall()

    # Prepare data and colors
    formatted_results = []
    row_colors = []
    for row in results:
        question_id, total_answered, total_correct, total_incorrect = row[:4]
        question_doc = questions_collection.find_one({"Question_No": question_id})
        age_group = question_doc.get("Age_Group", "N/A")
        topic = question_doc.get("Topic", "N/A")
        question_text = question_doc.get("Question_Text", "N/A")

        # Determine color by age group
        colors = {
            "1-5": "\033[92m",  # Green
            "5-10": "\033[94m",  # Blue
            "10-15": "\033[95m",  # Magenta
            "15-20": "\033[93m",  # Yellow
            "20-30": "\033[96m",  # Cyan
            "30-40": "\033[91m",  # Red
            "40-100": "\033[90m",  # Gray
        }
        row_colors.append(colors.get(age_group, "\033[0m"))

        # Add formatted row
        formatted_results.append([
            age_group,
            topic,
            question_id,
            question_text,
            total_correct,
            total_incorrect,
            total_answered,
        ])

    # Print the table with colors
    print_table(formatted_results, headers, column_widths, row_colors)
    sleep(5)
    main_menu()
#option 5:
def answered_correctly_count_list():
    """Retrieves data from Postgres and MongoDB and presents a table of correct answers answered by all users, from most to least"""
    pg_cursor.execute("SELECT * FROM players_list_by_correct_answers();")
    connection.commit()
    results = pg_cursor.fetchall()

    headers = ["Player ID", "Player Name", "Total Correct Answers"]
    column_widths = [20, 30, 25]  # Adjusted for better readability
    keys = ["player_id", "player_name", "total_correct_answers"]
    # Format results
    formatted_results = format_results(results, keys)

    # Print the table
    print("\n\033[92mCorrectly Answered Questions By Players:\033[0m\n")
    print_table(formatted_results, headers, column_widths)
    sleep(5)
    main_menu()
    #option 3:
def user_answers(player_id):
    """Retrieves data from Postgres and MongoDB and presents a full list of questions answered by the player"""
    pg_cursor.execute("SELECT * FROM show_questions_for_player(%s);", (player_id,))
    connection.commit()
    results = pg_cursor.fetchall()



    # Define table headers, keys, and column widths
    headers = ["Player ID", "Player Name", "Question ID", "Question Text", "Answered Correctly"]
    column_widths = [10, 20, 11, 120, 20]

    # Format results
    formatted_results = []
    for row in results:
        question_id = row["question_id"]
        question_doc = questions_collection.find_one({"Question_No": question_id})  # Fetch question text from MongoDB
        question_text = question_doc.get("Question_Text", "N/A") if question_doc else "N/A"

        # Prepare formatted row
        formatted_results.append([
            row["player_id"],
            row["player_name"],
            question_id,
            question_text,  # Limit question text to fit column
            "Correct" if row["is_correct"] else "Incorrect"  # Replace 'correct' with the actual key name
        ])

    # Print the table
    print(f"\n\033[92mQuestions Answered By Player {player_id}:\033[0m\n")
    print_table(formatted_results, headers, column_widths)
    sleep(5)
    main_menu()

#option 4:
def user_correct_answers(player_id):
    """Retrieves data from Postgres and MongoDB and presents a table of correct answers given by the player"""
    pg_cursor.execute("SELECT * from correct_answers_by_player(%s);",(player_id,))
    connection.commit()
    results = pg_cursor.fetchall()

    headers = ["Player ID", "Player Name", "Question ID", "Question Text", "Total Correct Answers"]
    column_widths = [10, 30, 11, 120, 21]

    formatted_results = []
    for row in results:
        question_id = row["question_id"]
        question_doc = questions_collection.find_one({"Question_No": question_id})  # Fetch question text from MongoDB
        question_text = question_doc.get("Question_Text", "N/A") if question_doc else "N/A"

        # Add formatted row
        formatted_results.append([
            row["player_id"],
            row["player_name"],
            question_id,
            question_text,  # Full question text
            row["total_correct_answers"]
        ])

        # Print the table
    print(f"\n\033[92mCorrect Answers By Player {player_id}:\033[0m\n")
    print_table(formatted_results, headers, column_widths)
    sleep(5)
    main_menu()

def get_mid_game_statistics(player_id):
    """Retrieves and prints mid-game statistics"""
    pg_cursor.execute("SELECT  * from mid_game_statistics(%s);", (player_id,))
    results = pg_cursor.fetchall()
    headers = ["Player ID", "Username", "Answered", "Correct", "Question ID", "Question Text", "Answer", "Is Correct",
               "Elapsed Time", "Score"]
    column_widths = [10, 20, 10, 10, 12, 120, 10, 12, 15, 8]
    formatted_results = []
    for row in results:
        question_id = row[4]

        question_doc = questions_collection.find_one({"Question_No": question_id})  # Confirm MongoDB field name
        question_text = question_doc.get("Question_Text", "Unknown") if question_doc else "Unknown"
        # question_text = questions_collection.find_one({"question_id":question_id},{"question_text":1})
        # question_text = question_text['question_text'] if question_text else "Unknown"
        formatted_row = [
            row[0],  # Player ID
            row[1],  # Username
            row[2],  # Answered Questions
            row[3],  # Correct Answers
            question_id,  # Question ID
            question_text,  # Question Text
            row[5],  # Selected Answer
            row[6],  # Is Correct
            row[7] or "N/A",  # Elapsed Time
            row[8] or "N/A",  # Score
        ]
        formatted_results.append(formatted_row)
    print_table(formatted_results, headers, column_widths)

#option 1:
def get_user_statistics(player_id):
    """Retrieves and shows the user's personal statistics from all games in the 'high_score' table"""
    pg_cursor.execute("SELECT * FROM show_user_statistics(%s);", (player_id,))
    connection.commit()
    results = pg_cursor.fetchall()
    headers = ["Player ID", "Username", "Questions Solved", "Started At", "Finished At", "Total Game Time", "Score"]
    column_widths = [10, 20, 20, 30, 30, 30, 10]

    # Format results for printing
    formatted_results = [
        [
            row["player_id"],
            row["username"],
            row.get("questions_solved", "N/A"),
            row.get("started_at", "N/A"),
            row.get("finished_at", "N/A"),
            row.get("total_game_time", "N/A"),
            row.get("score", "N/A"),
        ]
        for row in results
    ]

    # Use the generic print_table function
    print_table(formatted_results, headers, column_widths)
    sleep(5)
    return main_menu()

# option 2:
def get_user_best_score(player_id):
    """Retrieves and shows the user's personal best from all games"""
    pg_cursor.execute("SELECT * FROM show_user_best_score(%s);", (player_id,))
    result = pg_cursor.fetchone()  # Fetches only one row

    if result:
        # Define headers, keys, and column_widths directly for this specific function
        headers = ["Player ID", "Username", "Questions Solved", "Started At", "Finished At", "Total Game Time", "Score"]
        column_widths = [10, 20, 20, 30, 30, 30, 10]
        keys = ["player_id", "username", "questions_solved", "started_at", "finished_at", "total_game_time", "score"]

        # Format the single row as a list of results
        formatted_result = format_results([result], keys, default="N/A")

        # Print the result directly using print_table
        print_table(formatted_result, headers, column_widths)
    else:
        print("No best score found for this player.")

    sleep(5)
    return main_menu()

# option 6:
def show_high_score_table():
    """Shows the 'high_score' table"""
    pg_cursor.execute("SELECT * FROM show_high_score_table();")
    connection.commit()
    results = pg_cursor.fetchall()
    headers = ["Player ID", "Username", "Questions Solved", "Started At", "Finished At", "Total Game Time", "Score"]
    column_widths = [10, 20, 20, 30, 30, 30, 10]
    keys = ["player_id", "username", "questions_solved", "started_at", "finished_at", "total_game_time", "score"]

    # Format results using keys
    formatted_results = format_results(results, keys)

    # Call print_table directly
    print_table(formatted_results, headers, column_widths)
    sleep(5)
    main_menu()


#option 7:
def past_players():
    """Retrieves data from postgres and sends it to be printed as a table of past players"""
    pg_cursor.execute("SELECT * FROM past_players_list();")
    connection.commit()
    results = pg_cursor.fetchall()
    headers = ["Player ID", "Username", "Age", "Email", "Registration Date", "Total Players"]
    column_widths = [10, 20, 10, 30, 26, 15]
    keys = ["player_id", "username", "age", "email", "registration_date", "total_players"]

    # Format results using the new function
    formatted_results = format_results(results, keys)

    print_table(formatted_results, headers, column_widths)
    sleep(5)
    main_menu()

    sleep(5)
    return main_menu()

def check_to_quit(user_input, player_id = None):
    if user_input == 'q':
        if player_id:
            quit_game(player_id)

        return main_menu()
    return user_input

def get_age_group(age):
    """Determine the age group range for a given age"""

    age_groups = {
        "1-5": range(1,5),
        "5-10": range(5,10),
        "10-15": range(10,15),
        "15-20": range(15,20),
        "20-30": range(20,30),
        "30-40": range(30,40),
        "40-100": range(40,101)
    }
    for group, age_range in age_groups.items():
        if age in age_range:
            return group
    if not age in age_groups.items():
        print("No matching age groups for this age, please try again!")
        sleep(2)
        main_menu()




def quit_game (player_id):
    pg_cursor.execute("CALL update_session_time(%s);", (player_id,))
    connection.commit()
    print("Game session saved. You can resume later at any time")

def complete_game(player_id,player_age):
    """Completes the current game and asks the player if they want to start a new game or quit."""

    pg_cursor.execute("CALL update_high_score_table_when_quiz_finished(%s);", (player_id,))
    connection.commit()
    print("Congratulations! Game completed!")
    while True:
        new_or_quit = input(f"would you like to:\n"
                            f"\033[92m1. Play another game [Press N or 1]\n"
                            f"\033[94m2. Quit [Press Q or 2]\033[04").strip().lower()
        if new_or_quit.lower() in ('n','1'):
            topics = choose_topics(player_age)
            create_player_questions_set(player_id, get_age_group(player_age), topics)
            start_quiz(player_id, player_age)
            break
        elif new_or_quit in ('q','2'):
            print("Returning to main menu")
            (sleep(2))
            main_menu()
            break
        else:
            print("Invalid choice. Please enter N, 1, Q, or 2.")


def main_menu():
    print("Hello, and welcome to:".center(130, " "))  # Manually set the center width to 120
    time.sleep(2)

    # Limit to 10 cycles, for example
    for i, color in zip(range(5), itertools.cycle(colors)):
        text = f"{color}The Trivia Game!{reset}"
        print(f"\r{' '}\r{text.center(140)}", end="", flush=True)
        time.sleep(2)
    print("\n")  # Ensure the last line doesn't get overwritten

    while True:
        action = input("Please choose one of the options below:\n\n\
        1. New Player Sign-in [Press N]\n\
        2. Existing Player Log-in [Press E]\n\
        3. Show Statistics [Press S]\n\
        4. Quit the Game [Press Q]\n\n").lower()
        match action:
            case 'n' | '1':
                while True:
                    username = check_to_quit(input("Please enter a username: \n"))
                    if username.isdigit():
                        print("Username must contain characters!")
                        # username = check_to_quit(input("Please enter a username: \n"))
                        continue
                    password = check_to_quit(input("Please enter a password: \n"))
                    reenter_password = check_to_quit(input("Please re-enter your Password: \n"))

                    email = check_to_quit(input("Please enter your E-mail address: \n"))
                    try:
                        age= check_to_quit(int(input("Please enter your age: \n")))
                    except Exception as e:
                        print(f"An Error occurred with: '{e}'")
                        sleep(2)
                        return main_menu()
                    while password != reenter_password:
                        print("Passwords mismatched. Please try again.")
                        password = check_to_quit(input("Enter your password: \n"))
                        reenter_password = check_to_quit(input("Re-enter your password: \n"))


                    if password == reenter_password:
                        player_id = insert_new_player(username, password, email, age)
                        if player_id:
                            print(f"Player {username} created successfully with ID:\n{player_id} ")
                            selected_topics = choose_topics(age)
                            create_player_questions_set(player_id,get_age_group(age),selected_topics)
                            player_age = age
                            start_quiz(player_id, player_age)
                        else:
                            print("Failed to create player. Please try again.")
                            return main_menu()
                    else:
                        print("Passwords do not match. Please try again.")
                        sleep(2)
                        main_menu()


            case 'e' | '2':
                username = check_to_quit(input("Please enter a username: \n"))
                password = check_to_quit(input("Please enter a password: \n"))
                player_id, unfinished_game, player_age = verify_player(username,password)
                if player_id:
                    print(f"Welcome back, {username}!")
                    new_or_continue = input(f"Would you like to:\n"
                                            f"1. Start a New Game [Press 1 or N]\n"
                                            f"2. Continue an Existing Game [Press 2 or C]").strip().lower()
                    if new_or_continue in ('1','n'):
                        topics = choose_topics(player_age)
                        create_player_questions_set(player_id, get_age_group(player_age), topics)
                        start_quiz(player_id,player_age)
                    elif new_or_continue in ('2', 'c'):
                        if unfinished_game:
                            questions = fetch_remaining_questions(player_id)
                            start_quiz(player_id,player_age)
                        else:
                            print("No unfinished quiz found for this player. Starting a new game:")
                            topics = choose_topics(player_age)
                            create_player_questions_set(player_id, get_age_group(player_age), topics)
                            (sleep(2))
                            start_quiz(player_id,player_age)
                    else:
                        print("Invalid choice. Returning to main menu.")
                        main_menu()
                else:
                    print("Invalid login or finished game. Please try again")
                    sleep(2)
                    main_menu()
            case 's' | '3':
                present_statistics_menu()
            case 'q' | '4':
                print("Sorry to see you leave. Goodbye.")
                exit()


#
#
# def generate_topic_column_chart(questions_collection):
#     """Generates a column chart showing the percentage of players choosing each topic."""
#     # Aggregate to get the count of players choosing each topic in MongoDB
#     pipeline = [
#         {"$group": {"_id": "$Topic", "choice_count": {"$sum": 1}}},
#         {"$sort": {"choice_count": -1}}
#     ]
#     results = list(questions_collection.aggregate(pipeline))
#
#     topics = [res["_id"] for res in results]
#     choice_counts = [res["choice_count"] for res in results]
#     total_choices = sum(choice_counts)
#     percentages = [(count / total_choices) * 100 for count in choice_counts]
#
#     fig, ax = plt.subplots()
#     ax.bar(topics, percentages, color='skyblue')
#     ax.set_xlabel("Topics")
#     ax.set_ylabel("Percentage of Players (%)")
#     ax.set_title("Percentage of Players Choosing Each Topic")
#     plt.xticks(rotation=45, ha='right')  # Rotate topic labels for readability
#     plt.tight_layout()
#     plt.show()
#
# # Generate pie charts for each age group based on PostgreSQL data.
# generate_age_group_charts(pg_cursor, questions_collection)

# Generate a column chart for topics based on MongoDB data.
# generate_topic_column_chart(questions_collection)

# Comment out main_menu() for now to prevent it from overriding chart displays
# main_menu()

main_menu()

