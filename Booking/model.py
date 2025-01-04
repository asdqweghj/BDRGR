class ModelBooking:
    def __init__(self, db_model):
        self.conn = db_model.conn

    def add_booking(self, booking_id, user_id, facility_id, booking_date, start_time, end_time, status):
        c = self.conn.cursor()
        try:
            # Перевірка, чи існує user_id у таблиці user
            c.execute('SELECT 1 FROM "user" WHERE "user_id" = %s', (user_id,))
            user_exists = c.fetchone()

            if not user_exists:
                print("Error: User ID does not exist.")
                return False

            # Перевірка, чи існує facility_id у таблиці facility
            c.execute('SELECT 1 FROM "facility" WHERE "facility_id" = %s', (facility_id,))
            facility_exists = c.fetchone()

            if not facility_exists:
                print("Error: Facility ID does not exist.")
                return False

            # Додавання нового запису до таблиці booking
            c.execute(
                'INSERT INTO "booking" ("booking_id", "user_id", "facility_id", "booking_date", "start_time", "end_time", "status") '
                'VALUES (%s, %s, %s, %s, %s, %s, %s)',
                (booking_id, user_id, facility_id, booking_date, start_time, end_time, status)
            )
            self.conn.commit()
            return True
        except Exception as e:
            self.conn.rollback()
            print(f"Error With Adding A Booking: {str(e)}")
            return False

    def get_all_bookings(self):
        c = self.conn.cursor()
        try:
            # Отримання всіх записів з таблиці booking
            c.execute('SELECT * FROM "booking"')
            return c.fetchall()
        except Exception as e:
            print(f"Error With Retrieving Bookings: {str(e)}")
            return None

    def update_booking(self, booking_id, user_id, facility_id, booking_date, start_time, end_time, status):
        c = self.conn.cursor()
        try:
            # Перевірка, чи існує user_id у таблиці user
            c.execute('SELECT 1 FROM "user" WHERE "user_id" = %s', (user_id,))
            user_exists = c.fetchone()

            if not user_exists:
                print("Error: User ID does not exist.")
                return False

            # Перевірка, чи існує facility_id у таблиці facility
            c.execute('SELECT 1 FROM "facility" WHERE "facility_id" = %s', (facility_id,))
            facility_exists = c.fetchone()

            if not facility_exists:
                print("Error: Facility ID does not exist.")
                return False

            # Оновлення запису в таблиці booking
            c.execute(
                'UPDATE "booking" SET "user_id" = %s, "facility_id" = %s, "booking_date" = %s, "start_time" = %s, '
                '"end_time" = %s, "status" = %s WHERE "booking_id" = %s',
                (user_id, facility_id, booking_date, start_time, end_time, status, booking_id)
            )
            self.conn.commit()
            return True
        except Exception as e:
            self.conn.rollback()
            print(f"Error With Updating A Booking: {str(e)}")
            return False

    def delete_booking(self, booking_id):
        c = self.conn.cursor()
        try:
            # Видалення запису з таблиці booking
            c.execute('DELETE FROM "booking" WHERE "booking_id" = %s', (booking_id,))
            self.conn.commit()
            return True
        except Exception as e:
            self.conn.rollback()
            print(f"Error With Deleting A Booking: {str(e)}")
            return False

    def check_booking_existence(self, booking_id):
        c = self.conn.cursor()
        try:
            # Перевірка існування запису
            c.execute('SELECT 1 FROM "booking" WHERE "booking_id" = %s', (booking_id,))
            return bool(c.fetchone())
        except Exception as e:
            print(f"Error With Checking Booking Existence: {str(e)}")
            return False

    def create_booking_sequence(self):
        c = self.conn.cursor()
        try:
            # Створення або оновлення послідовності для booking_id
            c.execute("""
                DO $$
                DECLARE
                    max_id INT;
                BEGIN
                    -- Знаходимо максимальний booking_id
                    SELECT COALESCE(MAX(booking_id), 0) INTO max_id FROM "booking";

                    -- Перевіряємо, чи існує послідовність
                    IF NOT EXISTS (
                        SELECT 1 
                        FROM pg_sequences 
                        WHERE schemaname = 'public' AND sequencename = 'booking_id_seq'
                    ) THEN
                        -- Створення нової послідовності
                        EXECUTE 'CREATE SEQUENCE booking_id_seq START WITH ' || (max_id + 1);
                    ELSE
                        -- Оновлення існуючої послідовності
                        EXECUTE 'ALTER SEQUENCE booking_id_seq RESTART WITH ' || (max_id + 1);
                    END IF;
                END $$;
            """)
            self.conn.commit()
            return True
        except Exception as e:
            self.conn.rollback()
            print(f"Error With Creating Booking Sequence: {str(e)}")
            return False

    def generate_rand_booking_data(self, number_of_operations):
        c = self.conn.cursor()
        try:
            c.execute("""
              INSERT INTO "booking" ("booking_id", "booking_date", "start_time", "end_time", "status", "user_id", "facility_id")
            SELECT 
                nextval('booking_id_seq'), 
                -- Випадкова дата і час в межах 30 днів від сьогодні
                (CURRENT_DATE + (random() * 30)::int * interval '1 day') + (random() * interval '12 hours')::time AS booking_date,
                -- Випадковий час початку (з округленням до секунд)
                (CURRENT_TIME + (random() * interval '10 hours'))::time(2) AS start_time,
                -- Випадковий час завершення (на 2 години пізніше)
                ((CURRENT_TIME + (random() * interval '10 hours')) + interval '2 hours')::time(2) AS end_time,
                -- Випадковий статус
                (random() > 0.5)::boolean AS status,
                -- Випадковий user_id
                floor(random() * (SELECT max("user_id") FROM "Users") + 1)::integer AS user_id,
                -- Випадковий facility_id
                floor(random() * (SELECT max("facility_id") FROM "Facility") + 1)::integer AS facility_id
            FROM generate_series(1, %s);
            """, (number_of_operations,))
            self.conn.commit()
            return True
        except Exception as e:
            self.conn.rollback()
            print(f"Error With Generating Booking Data: {str(e)}")
            return False

    def truncate_booking_table(self):
        c = self.conn.cursor()
        try:
            # Очищення таблиці booking
            c.execute('DELETE FROM "booking"')
            self.conn.commit()
            return True
        except Exception as e:
            self.conn.rollback()
            print(f"Error With Truncating Booking Table: {str(e)}")
            return False