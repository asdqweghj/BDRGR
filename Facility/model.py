class ModelFacility:
    def __init__(self, db_model):
        self.conn = db_model.conn

    def add_facility(self, facility_id, facility_name, facility_type, venue_id):
        c = self.conn.cursor()
        try:
            # Перевірка, чи існує venue_id у таблиці venue
            c.execute('SELECT 1 FROM "venue" WHERE "venue_id" = %s', (venue_id,))
            venue_exists = c.fetchone()

            if not venue_exists:
                print("Error: Venue ID does not exist.")
                return False

            # Додавання нового запису до таблиці facility
            c.execute(
                'INSERT INTO "facility" ("facility_id", "facility_name", "facility_type", "venue_id") VALUES (%s, %s, %s, %s)',
                (facility_id, facility_name, facility_type, venue_id,)
            )
            self.conn.commit()
            return True
        except Exception as e:
            self.conn.rollback()
            print(f"Error With Adding A Facility: {str(e)}")
            return False

    def get_all_facilities(self):
        c = self.conn.cursor()
        try:
            # Отримання всіх записів з таблиці facility
            c.execute('SELECT * FROM "facility"')
            return c.fetchall()
        except Exception as e:
            print(f"Error With Retrieving Facilities: {str(e)}")
            return None

    def update_facility(self, facility_id, facility_name, facility_type, venue_id):
        c = self.conn.cursor()
        try:
            # Перевірка, чи існує venue_id у таблиці venue
            c.execute('SELECT 1 FROM "venue" WHERE "venue_id" = %s', (venue_id,))
            venue_exists = c.fetchone()

            if not venue_exists:
                print("Error: Venue ID does not exist.")
                return False

            # Оновлення запису в таблиці facility
            c.execute(
                'UPDATE "facility" SET "facility_name" = %s, "facility_type" = %s, "venue_id" = %s WHERE "facility_id" = %s',
                (facility_name, facility_type, venue_id, facility_id)
            )
            self.conn.commit()
            return True
        except Exception as e:
            self.conn.rollback()
            print(f"Error With Updating A Facility: {str(e)}")
            return False

    def delete_facility(self, facility_id):
        c = self.conn.cursor()
        try:
            # Видалення запису з таблиці facility
            c.execute('DELETE FROM "facility" WHERE "facility_id" = %s', (facility_id,))
            self.conn.commit()
            return True
        except Exception as e:
            self.conn.rollback()
            print(f"Error With Deleting A Facility: {str(e)}")
            return False

    def check_facility_existence(self, facility_id):
        c = self.conn.cursor()
        try:
            # Перевірка існування запису
            c.execute('SELECT 1 FROM "facility" WHERE "facility_id" = %s', (facility_id,))
            return bool(c.fetchone())
        except Exception as e:
            print(f"Error With Checking Facility Existence: {str(e)}")
            return False

    def create_facility_sequence(self):
        c = self.conn.cursor()
        try:
            # Створення або оновлення послідовності для facility_id
            c.execute("""
                DO $$
                DECLARE
                    max_id INT;
                BEGIN
                    -- Знаходимо максимальний facility_id
                    SELECT COALESCE(MAX(facility_id), 0) INTO max_id FROM "facility";

                    -- Перевіряємо, чи існує послідовність
                    IF NOT EXISTS (
                        SELECT 1 
                        FROM pg_sequences 
                        WHERE schemaname = 'public' AND sequencename = 'facility_id_seq'
                    ) THEN
                        -- Створення нової послідовності
                        EXECUTE 'CREATE SEQUENCE facility_id_seq START WITH ' || (max_id + 1);
                    ELSE
                        -- Оновлення існуючої послідовності
                        EXECUTE 'ALTER SEQUENCE facility_id_seq RESTART WITH ' || (max_id + 1);
                    END IF;
                END $$;
            """)
            self.conn.commit()
            return True
        except Exception as e:
            self.conn.rollback()
            print(f"Error With Creating Facility Sequence: {str(e)}")
            return False

    def generate_rand_facility_data(self, number_of_operations):
        c = self.conn.cursor()
        try:
            c.execute("""
                INSERT INTO "facility" ("facility_id", "facility_name", "facility_type", "venue_id")
                SELECT 
                    nextval('facility_id_seq'),
                    (array['Football', 'Basketball', 'Voleyball', 'Golf', 'Tennis'])[floor(random() * 5) + 1] AS facility_name,
                    CASE 
                        WHEN random() < 0.5 THEN 'Indoor'
                        ELSE 'Outdoor'
                    END AS facility_type,
                    floor(random() * (SELECT max("venue_id") FROM "venue") + 1)::int AS venue_id
                FROM generate_series(1, %s);
            """, (number_of_operations,))
            self.conn.commit()
            return True
        except Exception as e:
            self.conn.rollback()
            print(f"Error With Generating Facility Data: {str(e)}")
            return False

    def truncate_facility_table(self):
        c = self.conn.cursor()
        try:
            # Очищення таблиці facility
            c.execute('DELETE FROM "facility"')
            self.conn.commit()
            return True
        except Exception as e:
            self.conn.rollback()
            print(f"Error With Truncating Facility Table: {str(e)}")
            return False
