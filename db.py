 import psycopg2

conn = psycopg2.connect(
    dbname="DOG_FEEDER",
    user="postgres",
    password="1234",
    host="192.168.14.1",
    port="5432"
)

def log_entry(dog_name):
    with conn.cursor() as cur:
        
        cur.execute("SELECT id FROM dogs WHERE name=%s", (dog_name,))
        row = cur.fetchone()

        if row:
            dog_id = row[0]
        else:
            cur.execute(
                "INSERT INTO dogs (name) VALUES (%s) RETURNING id",
                (dog_name,)
            )
            dog_id = cur.fetchone()[0]

        
        cur.execute(
            "INSERT INTO feeding_logs (dog_id, entry_time) VALUES (%s, NOW()) RETURNING id",
            (dog_id,)
        )
        conn.commit()
        return cur.fetchone()[0]

def log_exit(log_id, food_grams):
    with conn.cursor() as cur:
        cur.execute(
            """
            UPDATE feeding_logs
            SET exit_time = NOW(),
                food_dispensed_grams = %s
            WHERE id = %s
            """,
            (food_grams, log_id)
        )
        conn.commit()
