import psycopg2 # pyright: ignore
import io
from babydragon.memory.threads.base_thread import BaseThread
from pydantic_core.core_schema import ExpectedSerializationTypes


memory = BaseThread()
memory.load('./parquets/base_test')
data = memory.memory_thread.to_struct('data')
tuples = [(d['role'], d['content'], d['timestamp'], d['tokens_count']) for d in data]
""" print(tuples) """





try:
    conn = psycopg2.connect(database="postgres",
                            host="db.nleiqequaduxvlmiitkk.supabase.co",
                            user="postgres",
                            password="Orsopolare091",
                            port="5432")
except Exception as e:
    print(e)
    conn = None


def create_conversation(conn, cur, nome):
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


def bulk_insert(conn,cur,nome, tuples):
    try:
        cur = conn.cursor()
        query = f"INSERT INTO conversations.{nome} (role, content, timestamp, tokens_count) VALUES (%s, %s, %s, %s)"
        cur.executemany(query, tuples)
        conn.commit()
        cur.close()
    except Exception as e:
        print(f'\nError during bulk insert into conversations.{nome}: {e}')
        cur.close()
        conn.rollback()


if conn is not None:
    
    create_conversation(conn, conn.cursor(), 'conversazione3')
    bulk_insert(conn, conn.cursor(), 'conversazione3', tuples)













