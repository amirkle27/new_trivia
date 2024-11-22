select count (*) from questions;
 select * from questions;


DROP FUNCTION IF EXISTS new_player;

CREATE OR REPLACE FUNCTION new_player(
    new_username VARCHAR(50),
    new_password TEXT,
    new_email VARCHAR(100),
    new_age INTEGER,
    OUT out_player_id INTEGER
)
LANGUAGE plpgsql AS
$$
BEGIN
    -- Check for existing username
    IF EXISTS(SELECT 1 FROM players WHERE players.username = new_username) THEN
        RAISE EXCEPTION 'This username already exists. Try something else';
    END IF;

    -- Check for existing password
    IF EXISTS(SELECT 1 FROM players WHERE players.password = new_password) THEN
        RAISE EXCEPTION 'This password already exists. Try something else';
    END IF;

    -- Check for existing email
    IF EXISTS(SELECT 1 FROM players WHERE players.email = new_email) THEN
        RAISE EXCEPTION 'This email already exists. Try something else';
    ELSE
        -- Insert into players and return player_id
        INSERT INTO players (username, password, email, age)
        VALUES (new_username, new_password, new_email, new_age)
        RETURNING player_id INTO out_player_id;
    END IF;
END;
$$;

drop function log_new_player;

CREATE OR REPLACE FUNCTION log_new_player()
    RETURNS TRIGGER AS $$
        begin
            INSERT INTO new_player_log (player_id) VALUES (NEW.player_id);
            RETURN NEW;
        end;
    $$ LANGUAGE plpgsql;

drop TRIGGER IF EXISTS new_user_registration ON players;

CREATE TRIGGER new_user_registration
AFTER INSERT ON players
FOR EACH ROW
EXECUTE FUNCTION log_new_player();

drop function get_random_questions;

CREATE OR REPLACE FUNCTION get_random_questions ()
    RETURNS TABLE (
        question_id INTEGER,
        question_text TEXT,
        answer_a TEXT,
        answer_b TEXT,
        answer_c TEXT,
        answer_d TEXT,
        correct_answer CHAR(1))
language plpgsql AS
    $$
    begin
        RETURN QUERY
        SELECT q.question_id, q.question_text, q.answer_a, q.answer_b, q.answer_c, q.answer_d, q.correct_answer
        FROM questions q
        ORDER BY RANDOM()
        LIMIT 20;
        END
    $$;


drop function retrieve_existing_player;

CREATE OR REPLACE FUNCTION retrieve_existing_player(
    IN p_username VARCHAR,
    IN p_password VARCHAR,
    OUT player_exists BOOLEAN,
    OUT player_id INTEGER,
    OUT unfinished_game BOOLEAN)
language plpgsql AS
    $$
    DECLARE
        v_password TEXT;
        v_player_id INTEGER;
        v_questions_answered INTEGER;
    begin
        SELECT p.player_id, p.password
        INTO v_player_id, v_password
        FROM players p
        WHERE p.username = p_username;

        IF v_player_id IS NOT NULL AND v_password = p_password THEN
            player_exists := TRUE;
            player_id := v_player_id;

            SELECT COUNT (*)
            INTO v_questions_answered
            FROM player_answers pa
            WHERE pa.player_id = v_player_id;

            unfinished_game := v_questions_answered < 20;
        ELSE
            player_exists := FALSE;
            unfinished_game := FALSE;

        end if;
    end;
        $$;

drop procedure update_player_answers;

CREATE OR REPLACE PROCEDURE update_player_answers(
    IN p_player_id INTEGER,
    IN p_question_id INTEGER,
    IN p_selected_answer CHAR(1),
    IN p_is_correct BOOLEAN)
language plpgsql AS
    $$
    begin
        INSERT INTO player_answers(player_id, question_id, selected_answer, is_correct)
        VALUES (p_player_id,p_question_id,p_selected_answer,p_is_correct)
        ON CONFLICT (player_id,question_id)
        DO UPDATE SET
            selected_answer = EXCLUDED.selected_answer,
            is_correct = EXCLUDED.is_correct;

        UPDATE players
        SET questions_solved=questions_solved+1
        WHERE player_id=p_player_id;
        UPDATE high_scores
        SET score=score+1
        WHERE player_id=player_id;

    end;

$$;


-- ALTER TABLE player_answers
-- DROP CONSTRAINT player_answers_question_id_fkey;

drop procedure update_high_score_table_start_time;

CREATE OR REPLACE procedure update_high_score_table_start_time(
    IN p_player_id INTEGER)
language plpgsql AS
    $$
        begin
            INSERT INTO high_scores (player_id, started_at)
            VALUES (p_player_id, CURRENT_TIMESTAMP);
        end;
    $$;


drop procedure update_high_score_table_when_quiz_finished;

CREATE OR REPLACE procedure update_high_score_table_when_quiz_finished(
    IN p_player_id INTEGER)
language plpgsql AS
    $$
    DECLARE v_correct_answer INTEGER;
            v_latest_score_id INTEGER;
        begin
            SELECT COUNT (*)
            INTO v_correct_answer
            FROM player_answers
            WHERE player_id = p_player_id AND is_correct = TRUE;

            IF v_correct_answer >= 5 THEN
                SELECT score_id
                INTO v_latest_score_id
                FROM high_scores
                WHERE player_id = p_player_id
                ORDER BY started_at DESC
                LIMIT 1;

                UPDATE high_scores
                SET finished_at = CURRENT_TIMESTAMP,
                    total_game_time = (CURRENT_TIMESTAMP - started_at),
                    score = v_correct_answer
                WHERE  score_id = v_latest_score_id;
            END IF;
        end;
    $$;


drop procedure update_session_time;

CREATE OR REPLACE PROCEDURE update_session_time(
    IN p_player_id INTEGER)
language plpgsql AS
    $$
    DECLARE
        v_current_session_time INTERVAL;
    begin
            -- Calculate the current session time by subtracting started_at from the current time
        v_current_session_time := CURRENT_TIMESTAMP -
                                    (SELECT COALESCE(started_at, CURRENT_TIMESTAMP)
                                     FROM high_scores
                                     WHERE player_id = p_player_id
                                     ORDER BY score_id
                                     DESC LIMIT 1);
        UPDATE high_scores
        SET session_duration = v_current_session_time,
            total_game_time = COALESCE(total_game_time, INTERVAL '0')+ v_current_session_time
        WHERE player_id = p_player_id
        AND finished_at IS NULL;
    end;
     $$;


drop function maintain_top_20_scores;

CREATE OR REPLACE FUNCTION maintain_top_20_scores()
RETURNS TRIGGER
language plpgsql AS
    $$
    begin
        DELETE FROM high_scores
        WHERE score_id NOT IN
              (SELECT score_id
                FROM high_scores
                ORDER BY score DESC
                LIMIT 20);
        RETURN NEW;
    end;
    $$;

drop TRIGGER limit_high_scores ON high_scores;

CREATE TRIGGER limit_high_scores
AFTER INSERT ON high_scores
FOR EACH ROW
EXECUTE FUNCTION maintain_top_20_scores();

drop function show_user_statistics;

CREATE OR REPLACE FUNCTION show_user_statistics(
    IN p_player_id INTEGER)
    RETURNS TABLE (
        player_id INTEGER,
        username VARCHAR(50),
        questions_solved INTEGER,
        started_at TIMESTAMP,
        finished_at TIMESTAMP,
        total_game_time INTERVAL,
        score INTEGER)
    language plpgsql AS
    $$
    begin
        RETURN QUERY
                SELECT hs.player_id, p.username, p.questions_solved, hs.started_at, hs.finished_at, hs.total_game_time, hs.score
                FROM high_scores hs
                JOIN players p
                ON hs.player_id = p.player_id
                WHERE hs.player_id=p_player_id;
    end;
    $$;

drop function mid_game_statistics;

CREATE OR REPLACE FUNCTION mid_game_statistics(
    IN p_player_id INTEGER)
RETURNS TABLE (
    player_id INTEGER,
    username VARCHAR,
    answered_questions INTEGER,
    correct_answers INTEGER,
    question_id INTEGER,
    selected_answer CHAR(1),
    is_correct BOOLEAN,
    elapsed_time INTERVAL,
    score INTEGER
)
LANGUAGE plpgsql AS
$$
BEGIN
    RETURN QUERY
        SELECT p.player_id,
               p.username,
               (SELECT COUNT(*)::INTEGER
                FROM player_answers pa
                WHERE pa.player_id = p.player_id) AS answered_questions,
               (SELECT COUNT(*)::INTEGER
                FROM player_answers pa
                WHERE pa.player_id = p_player_id AND pa.is_correct = TRUE) AS correct_answers,
               pa.question_id::INTEGER, -- Ensure question_id is explicitly cast to INTEGER
               pa.selected_answer,
               pa.is_correct,
               (CASE
                   WHEN hs.started_at IS NOT NULL THEN (NOW() - hs.started_at)::INTERVAL

                END) AS elapsed_time,
               hs.score
        FROM players p
        LEFT JOIN player_answers pa ON p.player_id = pa.player_id
        LEFT JOIN high_scores hs ON p.player_id = hs.player_id
        WHERE p.player_id = p_player_id;
END;
$$;
--  AND hs.finished_at IS NULL


drop function show_user_best_score;
SELECT * FROM show_user_statistics(80);


select * from players;

CREATE OR REPLACE FUNCTION show_user_best_score(
    IN p_player_id INTEGER
)
RETURNS TABLE (
    player_id INT,
    username VARCHAR,
    questions_solved INT,
    started_at TIMESTAMP,
    finished_at TIMESTAMP,
    total_game_time INTERVAL,
    score INTEGER)
    language plpgsql AS
$$
begin
    RETURN QUERY
    SELECT hs.player_id, p.username, p.questions_solved, hs.started_at, hs.finished_at, hs.total_game_time, hs.score
    FROM high_scores hs
    JOIN players p ON hs.player_id = p.player_id
    WHERE hs.player_id = p_player_id
    ORDER BY hs.score DESC
    LIMIT 1;
end;
$$;



drop function show_high_score_table;

CREATE OR REPLACE FUNCTION show_high_score_table()
    RETURNS TABLE (
        player_id INTEGER,
        username VARCHAR(50),
        questions_solved INTEGER,
        started_at TIMESTAMP,
        finished_at TIMESTAMP,
        total_game_time INTERVAL,
        score integer)
    language plpgsql AS
    $$
    begin
        RETURN QUERY
                SELECT hs.player_id, p.username, p.questions_solved, hs.started_at, hs.finished_at, hs.total_game_time, hs.score
                FROM high_scores hs
                JOIN players p
                ON hs.player_id = p.player_id;
    end;
$$;

drop function past_players_list;

CREATE OR REPLACE FUNCTION past_players_list()
    RETURNS TABLE (
        player_id INTEGER,
        username VARCHAR(50),
        age INTEGER,
        email VARCHAR(100),
        registration_date TIMESTAMP,
        total_players INTEGER)
language plpgsql AS
    $$
    DECLARE  v_total_players INTEGER;
begin
    SELECT COUNT(*) INTO v_total_players FROM players ;

    RETURN QUERY
        SELECT p.player_id, p.username, p.age, p.email, MIN(hs.started_at) AS registration_date, v_total_players
        FROM players p
        LEFT JOIN high_scores hs
        ON  p.player_id = hs.player_id
        GROUP BY p.player_id, p.username, p.age, p.email
        ORDER BY registration_date DESC;
end;
    $$;

SELECT * FROM most_least_answered_questions();








DROP FUNCTION IF EXISTS most_least_answered_questions;

CREATE OR REPLACE FUNCTION most_least_answered_questions()
RETURNS TABLE (
    question_id INTEGER,
    total_answered_times INTEGER,
    total_correct_times INTEGER,
    total_incorrect_times INTEGER
) LANGUAGE plpgsql AS
$$
BEGIN
    RETURN QUERY
        SELECT
            pa.question_id,  -- Explicitly use table alias
            COUNT(*)::INTEGER AS total_answered_questions,
            SUM(CASE WHEN pa.is_correct THEN 1 ELSE 0 END)::INTEGER AS total_correct_answers,
            SUM(CASE WHEN NOT pa.is_correct THEN 1 ELSE 0 END)::INTEGER AS total_incorrect_answers
        FROM player_answers pa
        GROUP BY pa.question_id  -- Use the alias here as well
        ORDER BY total_answered_questions DESC;
END;
$$;

drop function correct_answers_by_player;

CREATE OR REPLACE FUNCTION correct_answers_by_player(
    IN p_player_id INTEGER
)

RETURNS TABLE (
                player_id INTEGER,
                player_name VARCHAR(50),
                question_id INTEGER,
                total_correct_answers INTEGER
              )
language plpgsql AS
    $$
    begin
        RETURN QUERY
            SELECT
                p.player_id,
                p.username AS player_name,
                pa.question_id,
                (SELECT COUNT(*)::INTEGER
                FROM player_answers pa_inner
                WHERE pa_inner.player_id = p_player_id
                AND pa_inner.is_correct = TRUE) AS total_correct_answers
            FROM players p
            JOIN player_answers pa
            ON p.player_id = pa.player_id
            WHERE pa.is_correct = TRUE
            AND pa.player_id = p_player_id;
        end;
            $$;

drop function players_list_by_correct_answers;

CREATE OR REPLACE FUNCTION players_list_by_correct_answers()
RETURNS TABLE (
                player_id INTEGER,
                player_name VARCHAR(50),
                total_correct_answers INTEGER
              )
language plpgsql AS
    $$
    begin
        RETURN QUERY
            SELECT
                p.player_id,
                p.username AS player_name,
                COUNT(pa.question_id)::INTEGER AS total_correct_answers
            FROM players p
            JOIN player_answers pa
            ON p.player_id = pa.player_id
            WHERE pa.is_correct = TRUE
            GROUP BY p.player_id
            ORDER BY total_correct_answers DESC;
        end;
            $$;
select * from players_list_by_correct_answers(80);
drop function show_questions_for_player;

CREATE OR REPLACE FUNCTION show_questions_for_player(
    IN p_player_id INTEGER
                )
RETURNS TABLE
            (player_id INTEGER,
             player_name VARCHAR(50),
             question_id INTEGER,
             is_correct BOOLEAN)
language plpgsql AS
    $$
    begin
        RETURN QUERY
                SELECT p.player_id,
                       p.username AS player_name,
                       pa. question_id,
                       pa. is_correct
                FROM players p
                JOIN player_answers pa
                ON p.player_id = pa.player_id
                WHERE p_player_id = p.player_id
                ORDER BY pa.question_id;
    end
    $$;

CREATE VIEW correct_players AS
    SELECT * FROM players_list_by_correct_answers();

CREATE VIEW most_answered_questions AS
    SELECT * FROM most_least_answered_questions();

CREATE VIEW past_players AS
    SELECT * FROM past_players_list();

SELECT * FROM players
-- drop function most_least_answered_questions;
--
-- CREATE OR REPLACE FUNCTION most_least_answered_questions()
--     RETURNS TABLE (
--         question_id INTEGER,
--         total_answered_questions INTEGER,
--         total_correct_answers INTEGER,
--         total_incorrect_answers INTEGER
--                   )
--     language plpgsql AS
--     $$
-- begin
--     RETURN QUERY
--         SELECT
--             question_id,
--             COUNT(*) AS total_answered_questions,
--             SUM(CASE WHEN pa.is_correct THEN 1 ELSE 0 END) AS total_correct_answeres,
--             SUM(CASE WHEN NOT pa.is_correct THEN 1 ELSE 0 END) AS total_incorrect_answers
--         FROM player_answers pa
--         GROUP BY question_id
--         ORDER BY total_answered_questions DESC;
-- end;
-- $$;



SELECT setval('players_player_id_seq', (SELECT MAX(player_id) FROM players));
DELETE FROM players;
select * from players;
select * from player_answers;
select * from new_player_log;
select * from high_scores;
select * from questions;
ALTER SEQUENCE players_player_id_seq RESTART WITH 1;

-- drop procedure add_answer_to_player_answers
--f
-- CREATE OR REPLACE PROCEDURE add_answer_to_player_answers()

drop table trivia_statistics;
CREATE TABLE trivia_statistics (
    age_group VARCHAR(10),
    correct_answers INT DEFAULT 0,
    incorrect_answers INT DEFAULT 0
);
select * from trivia_statistics
