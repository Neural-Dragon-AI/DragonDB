import psycopg2 # pyright: ignore
from babydragon.memory.threads.base_thread import BaseThread

def connect_to_supabase():
    try:
        return psycopg2.connect(database="postgres",
                                host="db.nleiqequaduxvlmiitkk.supabase.co",
                                user="postgres",
                                password="Orsopolare091",
                                port="5432")
    except Exception as e:
        print(e)
        return None


def create_conversation(conn, nome):
    cur = conn.cursor()
    try:
        create_table_query = f"""
        CREATE TABLE conversations.{nome} (
        role TEXT NULL,
        content TEXT NULL,
        timestamp BIGINT NOT NULL PRIMARY KEY,
        tokens_count BIGINT NULL
        );
        """
        cur.execute(create_table_query)
        conn.commit()
        cur.close()
        print(f"conversation.{nome} created in Supabase.")
    except Exception as e:
        print(f'\nError during creation of conversations.{nome}: {e}')
        cur.close()
        conn.rollback()


def bulk_insert(conn,nome, tuples):
    cur = conn.cursor()
    try:
        query = f"INSERT INTO conversations.{nome} (role, content, timestamp, tokens_count) VALUES (%s, %s, %s, %s)"
        cur.executemany(query, tuples)
        print(f"Bulked in all data in {nome}")
        conn.commit()
        cur.close()
    except Exception as e:
        print(f'\nError during bulk insert into conversations.{nome}: {e}')
        cur.close()
        conn.rollback()


def create_conversation_data(url):
    memory = BaseThread()
    memory.load_from_gpt_url(url)
    data = memory.memory_thread.to_struct('data')
    tuples = [(d['role'], d['content'], d['timestamp'], d['tokens_count']) for d in data]
    return tuples













