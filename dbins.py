import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "billease.db")

products = [
    ("Black Rose", "33059040", 0, 18),
    ("Colour Matte", "33059040", 0, 18),
    ("C Matt 30ml", "33059040", 0, 18),
    ("C Matt 60ml", "33059040", 0, 18),
    ("Fruti Pouch", "33059040", 0, 18),

    ("Kavari Cone", "14049090", 0, 5),
    ("Neeta Cone", "14049090", 0, 5),
    ("K Bridal", "14049090", 0, 5),
    ("Nazify Cone", "14049090", 0, 5),
    ("Zameen Cone", "14049090", 0, 5),

    ("HR Cream Block", "33079010", 0, 18),

    ("Nisha Block", "33059040", 0, 18),
    ("Nisha Burgundy", "33059040", 0, 18),
    ("Nisha Brown", "33059040", 0, 18),
    ("Nisha Shampoo", "33059040", 0, 18),
    ("Nisha Nature Matt Cream", "33059040", 0, 18),

    ("Nisha Siram", "33059090", 0, 18),
    ("Multani Mitti", "33049990", 0, 18),
    ("Shampoo Bottle", "33051090", 0, 18),
    ("Nisha Soap", "34011190", 0, 18),

    ("Zipper Cone", "33059040", 0, 18),
    ("Kavari Powder", "33059040", 0, 18),

    ("Nature Matt 10Rs", "33059030", 0, 18),
    ("Easy Fast 10Rs", "33059030", 0, 18),
    ("Easy Fast 20Rs", "33059030", 0, 18),

    ("Kavari Shampoo", "33059090", 0, 18),
    ("K Siram", "33059040", 0, 18),

    ("Nisha Cream 30Rs", "24012000", 0, 18),

    ("Handwash 675ml", "34012000", 0, 18),
    ("Handwash 200ml", "34012000", 0, 18),

    ("Rose Water", "33030020", 0, 18),
    ("Sunscreen Lotion 60Rs", "33079010", 0, 18),

    ("Kavari Box 99Rs", "33059030", 0, 18),
    ("Nisha Cream Box 150", "33059030", 0, 18),
]


def main():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    inserted = 0

    for name, hsn, price, gst in products:

        cur.execute("""
            SELECT id
            FROM catalogue
            WHERE lower(name)=lower(?)
        """, (name,))

        if not cur.fetchone():
            cur.execute("""
                INSERT INTO catalogue
                (name, hsn_code, price, gst_rate)
                VALUES (?, ?, ?, ?)
            """, (name, hsn, price, gst))

            inserted += 1

    conn.commit()
    conn.close()

    print(f"{inserted} products inserted successfully.")


if __name__ == "__main__":
    main()