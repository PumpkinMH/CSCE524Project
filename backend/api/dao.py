from django.db import connection

def _map_results(cursor):
    """Helper function to map raw SQL tuples into Python dictionaries."""
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]

class MedicationDAO:
    
    @staticmethod
    def create(name, med_type, strength, condition_treated, instructions, amount_left, refill_threshold, is_active=True):
        query = """
            INSERT INTO medications (name, medication_type, strength, condition_treated, instructions, amount_left, refill_threshold, is_active)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING medication_id;
        """
        with connection.cursor() as cursor:
            cursor.execute(query, [name, med_type, strength, condition_treated, instructions, amount_left, refill_threshold, is_active])
            return cursor.fetchone()[0] # Returns the newly generated UUID

    @staticmethod
    def get_all():
        query = "SELECT * FROM medications ORDER BY name ASC;"
        with connection.cursor() as cursor:
            cursor.execute(query)
            return _map_results(cursor)

    @staticmethod
    def get_by_id(medication_id):
        query = "SELECT * FROM medications WHERE medication_id = %s;"
        with connection.cursor() as cursor:
            cursor.execute(query, [medication_id])
            results = _map_results(cursor)
            return results[0] if results else None

    @staticmethod
    def update(medication_id, amount_left, is_active):
        """Example update focusing on inventory and status."""
        query = """
            UPDATE medications 
            SET amount_left = %s, is_active = %s
            WHERE medication_id = %s;
        """
        with connection.cursor() as cursor:
            cursor.execute(query, [amount_left, is_active, medication_id])
            
    @staticmethod
    def delete(medication_id):
        query = "DELETE FROM medications WHERE medication_id = %s;"
        with connection.cursor() as cursor:
            cursor.execute(query, [medication_id])


class ScheduleDAO:

    @staticmethod
    def create(medication_id, frequency_type, frequency_value, reminder_times):
        query = """
            INSERT INTO schedules (medication_id, frequency_type, frequency_value, reminder_times)
            VALUES (%s, %s, %s, %s)
            RETURNING schedule_id;
        """
        with connection.cursor() as cursor:
            # psycopg2 automatically handles Python lists to PostgreSQL ARRAYs
            cursor.execute(query, [medication_id, frequency_type, frequency_value, reminder_times])
            return cursor.fetchone()[0]

    @staticmethod
    def get_for_medication(medication_id):
        query = "SELECT * FROM schedules WHERE medication_id = %s;"
        with connection.cursor() as cursor:
            cursor.execute(query, [medication_id])
            return _map_results(cursor)

    @staticmethod
    def update(schedule_id, frequency_type, reminder_times):
        query = """
            UPDATE schedules 
            SET frequency_type = %s, reminder_times = %s
            WHERE schedule_id = %s;
        """
        with connection.cursor() as cursor:
            cursor.execute(query, [frequency_type, reminder_times, schedule_id])

    @staticmethod
    def delete(schedule_id):
        query = "DELETE FROM schedules WHERE schedule_id = %s;"
        with connection.cursor() as cursor:
            cursor.execute(query, [schedule_id])


class DoseLogDAO:

    @staticmethod
    def create(medication_id, scheduled_datetime, scheduled_strength, scheduled_quantity):
        query = """
            INSERT INTO dose_logs (medication_id, scheduled_datetime, scheduled_strength, scheduled_quantity, status)
            VALUES (%s, %s, %s, %s, 'pending')
            RETURNING log_id;
        """
        with connection.cursor() as cursor:
            cursor.execute(query, [medication_id, scheduled_datetime, scheduled_strength, scheduled_quantity])
            return cursor.fetchone()[0]

    @staticmethod
    def get_pending_logs():
        """A JOIN query to get pending doses along with the medication name."""
        query = """
            SELECT d.log_id, m.name, d.scheduled_datetime, d.scheduled_strength 
            FROM dose_logs d
            JOIN medications m ON d.medication_id = m.medication_id
            WHERE d.status = 'pending'
            ORDER BY d.scheduled_datetime ASC;
        """
        with connection.cursor() as cursor:
            cursor.execute(query)
            return _map_results(cursor)

    @staticmethod
    def get_logs_for_date(target_date):
        """Fetches all dose logs for a specific date, joining the medication name."""
        query = """
            SELECT d.log_id, m.name, d.scheduled_datetime, d.status 
            FROM dose_logs d
            JOIN medications m ON d.medication_id = m.medication_id
            WHERE DATE(d.scheduled_datetime AT TIME ZONE 'UTC') = %s
            ORDER BY d.scheduled_datetime ASC;
        """
        with connection.cursor() as cursor:
            cursor.execute(query, [target_date])
            # Uses the _map_results helper function we created earlier
            return _map_results(cursor)

    @staticmethod
    def mark_as_taken(log_id, actual_datetime_taken, actual_strength, actual_quantity):
        query = """
            UPDATE dose_logs 
            SET status = 'taken', 
                actual_datetime_taken = %s, 
                actual_strength_taken = %s, 
                actual_quantity_taken = %s
            WHERE log_id = %s;
        """
        with connection.cursor() as cursor:
            cursor.execute(query, [actual_datetime_taken, actual_strength, actual_quantity, log_id])

    @staticmethod
    def delete(log_id):
        query = "DELETE FROM dose_logs WHERE log_id = %s;"
        with connection.cursor() as cursor:
            cursor.execute(query, [log_id])