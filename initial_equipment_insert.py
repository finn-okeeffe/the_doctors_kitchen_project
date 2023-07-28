import psycopg2 as pg2
import secret
conn = pg2.connect(database="the_doctors_kitchen", user=secret.username, password=secret.password)
conn.close()