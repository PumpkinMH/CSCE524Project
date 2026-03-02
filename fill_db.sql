-- 1. Insert 3 Users
INSERT INTO users (user_id, email, password_hash, first_name, timezone) VALUES
('11111111-1111-1111-1111-111111111111', 'mabel@example.com', 'hashed_password_1', 'Mabel', 'America/New_York'),
('22222222-2222-2222-2222-222222222222', 'john.doe@example.com', 'hashed_password_2', 'John', 'America/Chicago'),
('33333333-3333-3333-3333-333333333333', 'sarah.smith@example.com', 'hashed_password_3', 'Sarah', 'America/Los_Angeles');

-- 2. Insert 4 Medications (2 for Mabel, 1 for John, 1 for Sarah)
INSERT INTO medications (medication_id, user_id, name, medication_type, strength, condition_treated, instructions, amount_left, refill_threshold, is_active, treatment_duration_days) VALUES
('44444444-4444-4444-4444-444444444441', '11111111-1111-1111-1111-111111111111', 'Lisinopril', 'tablet', '10mg', 'Blood Pressure', 'Take with a full glass of water', 20, 5, TRUE, 365),
('44444444-4444-4444-4444-444444444442', '11111111-1111-1111-1111-111111111111', 'Vitamin D3', 'capsule', '5000 IU', 'Supplement', 'Take with a meal', 60, 10, TRUE, 365),
('44444444-4444-4444-4444-444444444443', '22222222-2222-2222-2222-222222222222', 'Amoxicillin', 'capsule', '500mg', 'Infection', 'Take until completely finished', 4, 0, TRUE, 10),
('44444444-4444-4444-4444-444444444444', '33333333-3333-3333-3333-333333333333', 'Ibuprofen', 'tablet', '200mg', 'Pain Relief', 'Take as needed for pain', 40, 5, TRUE, 30);

-- 3. Insert 4 Schedules
INSERT INTO schedules (schedule_id, medication_id, frequency_type, frequency_value, reminder_times) VALUES
('55555555-5555-5555-5555-555555555551', '44444444-4444-4444-4444-444444444441', 'daily', '1', ARRAY['08:00:00']::TIME[]),
('55555555-5555-5555-5555-555555555552', '44444444-4444-4444-4444-444444444442', 'daily', '1', ARRAY['09:00:00']::TIME[]),
('55555555-5555-5555-5555-555555555553', '44444444-4444-4444-4444-444444444443', 'interval', 'twice daily', ARRAY['08:00:00', '20:00:00']::TIME[]),
('55555555-5555-5555-5555-555555555554', '44444444-4444-4444-4444-444444444444', 'as_needed', 'every 6 hours', ARRAY[]::TIME[]);

-- 4. Insert 42 Dose Logs to easily clear the 50 row minimum across all tables combined
INSERT INTO dose_logs (medication_id, scheduled_datetime, actual_datetime_taken, scheduled_strength, actual_strength_taken, scheduled_quantity, actual_quantity_taken, status, notes)
SELECT 
    '44444444-4444-4444-4444-444444444441', -- Mabel's Lisinopril
    gen_date + TIME '08:00:00',
    gen_date + TIME '08:15:00',
    '10mg', '10mg', 1, 1, 'taken', NULL
FROM generate_series(CURRENT_DATE - INTERVAL '14 days', CURRENT_DATE - INTERVAL '1 day', '1 day'::interval) AS gen_date;

INSERT INTO dose_logs (medication_id, scheduled_datetime, actual_datetime_taken, scheduled_strength, actual_strength_taken, scheduled_quantity, actual_quantity_taken, status, notes)
SELECT 
    '44444444-4444-4444-4444-444444444442', -- Mabel's Vitamin D
    gen_date + TIME '09:00:00',
    gen_date + TIME '09:05:00',
    '5000 IU', '5000 IU', 1, 1, 'taken', 'Took with breakfast'
FROM generate_series(CURRENT_DATE - INTERVAL '14 days', CURRENT_DATE - INTERVAL '1 day', '1 day'::interval) AS gen_date;

INSERT INTO dose_logs (medication_id, scheduled_datetime, actual_datetime_taken, scheduled_strength, actual_strength_taken, scheduled_quantity, actual_quantity_taken, status, notes)
SELECT 
    '44444444-4444-4444-4444-444444444443', -- John's Amoxicillin (Morning Dose)
    gen_date + TIME '08:00:00',
    gen_date + TIME '07:50:00',
    '500mg', '500mg', 1, 1, 'taken', NULL
FROM generate_series(CURRENT_DATE - INTERVAL '7 days', CURRENT_DATE - INTERVAL '1 day', '1 day'::interval) AS gen_date;

INSERT INTO dose_logs (medication_id, scheduled_datetime, actual_datetime_taken, scheduled_strength, actual_strength_taken, scheduled_quantity, actual_quantity_taken, status, notes)
SELECT 
    '44444444-4444-4444-4444-444444444443', -- John's Amoxicillin (Evening Dose)
    gen_date + TIME '20:00:00',
    gen_date + TIME '20:30:00',
    '500mg', '500mg', 1, 1, 'taken', NULL
FROM generate_series(CURRENT_DATE - INTERVAL '7 days', CURRENT_DATE - INTERVAL '1 day', '1 day'::interval) AS gen_date;
