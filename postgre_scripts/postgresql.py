import psycopg2 # pyright: ignore
""" from babydragon.memory.threads.base_thread import BaseThread """

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


def create_conversation(conn, conversation_id):
    cur = conn.cursor()
    try:
        create_table_query = f"""
        CREATE TABLE conversations.{conversation_id} (
        conversation_id TEXT NULL,
        conversation_title TEXT NULL,
        message_id TEXT NULL,
        parent_id TEXT NULL,
        upload_time BIGINT NULL,
        create_time BIGINT NOT NULL PRIMARY KEY,
        update_time BIGINT NULL,
        role TEXT NULL,
        content TEXT NULL,
        tokens_count BIGINT NULL
        );
        """
        cur.execute(create_table_query)
        conn.commit()
        cur.close()
        print(f"conversation.{conversation_id} created in Supabase.")
    except Exception as e:
        print(f'\nError during creation of conversations.{conversation_id}: {e}')
        cur.close()
        conn.rollback()


def bulk_insert(conn,conversation_id, tuples):
    cur = conn.cursor()
    try:
        query = f"INSERT INTO conversations.{conversation_id}\
        (conversation_id, conversation_title, message_id, parent_id, upload_time, create_time, update_time,\
        role, content, tokens_count)\
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s ,%s, %s)"
        cur.executemany(query, tuples)
        print(f"Bulked in all data in {conversation_id}")
        conn.commit()
        cur.close()
    except Exception as e:
        print(f'\nError during bulk insert into conversations.{conversation_id}: {e}')
        cur.close()
        conn.rollback()


def create_conversation_data(base_thread):
    data = base_thread.memory_thread.to_struct('data')
    tuples = [(d['conversation_id'], d['conversation_title'], d['message_id'], d['parent_id'], d['upload_time'],\
               d['create_time'], d['update_time'], d['role'], d['content'], d['tokens_count']) for d in data]
    return tuples













