class ModelPayment:
    def __init__(self, db_model):
        self.conn = db_model.conn

    def add_payment(self, payment_id, booking_id, amount, payment_date, payment_status):
        c = self.conn.cursor()
        try:
            # Перевірка, чи існує booking_id у таблиці booking
            c.execute('SELECT 1 FROM "booking" WHERE "booking_id" = %s', (booking_id,))
            booking_exists = c.fetchone()

            if not booking_exists:
                print("Error: Booking ID does not exist.")
                return False

            # Додавання нового запису до таблиці payment
            c.execute(
                'INSERT INTO "payment" ("payment_id", "booking_id", "amount", "payment_date", "payment_status") VALUES (%s, %s, %s, %s, %s)',
                (payment_id, booking_id, amount, payment_date, payment_status)
            )
            self.conn.commit()
            return True
        except Exception as e:
            self.conn.rollback()
            print(f"Error With Adding A Payment: {str(e)}")
            return False

    def get_all_payments(self):
        c = self.conn.cursor()
        try:
            # Отримання всіх записів з таблиці payment
            c.execute('SELECT * FROM "payment"')
            return c.fetchall()
        except Exception as e:
            print(f"Error With Retrieving Payments: {str(e)}")
            return None

    def update_payment(self, payment_id, booking_id, amount, payment_date, payment_status):
        c = self.conn.cursor()
        try:
            # Перевірка, чи існує booking_id у таблиці booking
            c.execute('SELECT 1 FROM "booking" WHERE "booking_id" = %s', (booking_id,))
            booking_exists = c.fetchone()

            if not booking_exists:
                print("Error: Booking ID does not exist.")
                return False

            # Оновлення запису в таблиці payment
            c.execute(
                'UPDATE "payment" SET "booking_id" = %s, "amount" = %s, "payment_date" = %s, "payment_status" = %s WHERE "payment_id" = %s',
                (booking_id, amount, payment_date, payment_status, payment_id)
            )
            self.conn.commit()
            return True
        except Exception as e:
            self.conn.rollback()
            print(f"Error With Updating A Payment: {str(e)}")
            return False

    def delete_payment(self, payment_id):
        c = self.conn.cursor()
        try:
            # Видалення запису з таблиці payment
            c.execute('DELETE FROM "payment" WHERE "payment_id" = %s', (payment_id,))
            self.conn.commit()
            return True
        except Exception as e:
            self.conn.rollback()
            print(f"Error With Deleting A Payment: {str(e)}")
            return False

    def check_payment_existence(self, payment_id):
        c = self.conn.cursor()
        try:
            # Перевірка існування запису
            c.execute('SELECT 1 FROM "payment" WHERE "payment_id" = %s', (payment_id,))
            return bool(c.fetchone())
        except Exception as e:
            print(f"Error With Checking Payment Existence: {str(e)}")
            return False

    def create_payment_sequence(self):
        c = self.conn.cursor()
        try:
            # Створення або оновлення послідовності для payment_id
            c.execute("""
                DO $$
                DECLARE
                    max_id INT;
                BEGIN
                    -- Знаходимо максимальний payment_id
                    SELECT COALESCE(MAX(payment_id), 0) INTO max_id FROM "payment";

                    -- Перевіряємо, чи існує послідовність
                    IF NOT EXISTS (
                        SELECT 1 
                        FROM pg_sequences 
                        WHERE schemaname = 'public' AND sequencename = 'payment_id_seq'
                    ) THEN
                        -- Створення нової послідовності
                        EXECUTE 'CREATE SEQUENCE payment_id_seq START WITH ' || (max_id + 1);
                    ELSE
                        -- Оновлення існуючої послідовності
                        EXECUTE 'ALTER SEQUENCE payment_id_seq RESTART WITH ' || (max_id + 1);
                    END IF;
                END $$;
            """)
            self.conn.commit()
            return True
        except Exception as e:
            self.conn.rollback()
            print(f"Error With Creating Payment Sequence: {str(e)}")
            return False

    def generate_rand_payment_data(self, number_of_operations):
        c = self.conn.cursor()
        try:
            c.execute("""
                INSERT INTO "payment" ("payment_id", "booking_id", "amount", "payment_date", "payment_status")
                SELECT 
                    nextval('payment_id_seq'),
                    floor(random() * (COALESCE((SELECT max("booking_id") FROM "booking"), 1)) + 1)::int AS booking_id,
                    round((random() * 100 + 50)::numeric, 2) AS amount,
                    clock_timestamp() - (random() * interval '30 days') AS payment_date,
                    CASE 
                        WHEN random() < 0.5 THEN true
                        ELSE false
                    END AS payment_status
                FROM generate_series(1, %s);
            """, (number_of_operations,))
            self.conn.commit()
            return True
        except Exception as e:
            self.conn.rollback()
            print(f"Error With Generating Payment Data: {str(e)}")
            return False

    def truncate_payment_table(self):
        c = self.conn.cursor()
        try:
            # Очищення таблиці payment
            c.execute('DELETE FROM "payment"')
            self.conn.commit()
            return True
        except Exception as e:
            self.conn.rollback()
            print(f"Error With Truncating Payment Table: {str(e)}")
            return False
