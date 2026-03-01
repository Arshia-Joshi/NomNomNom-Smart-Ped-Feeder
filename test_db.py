import psycopg2

conn = psycopg2.connect(
    dbname="dog_feeder",
    user="postgres",
    password="1234",
    host="192.168.29.186",
    port="5432"
)

cur = conn.cursor()

# Insert a test dog
cur.execute("INSERT INTO dogs (name) VALUES (%s) RETURNING id", ("TestDog",))
dog_id = cur.fetchone()[0]

# Insert feeding log
cur.execute("""
    INSERT INTO feeding_logs (dog_id)
    VALUES (%s)
    RETURNING id
""", (dog_id,))
log_id = cur.fetchone()[0]

# Simulate exit + food
cur.execute("""
    UPDATE feeding_logs
    SET exit_time = NOW(),
        food_dispensed_grams = %s
    WHERE id = %s
""", (120.5, log_id))

conn.commit()
cur.close()
conn.close()

print("Test insert successful!")