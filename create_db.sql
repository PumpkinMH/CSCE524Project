-- Drop existing tables to start fresh
DROP TABLE IF EXISTS dose_logs CASCADE;
DROP TABLE IF EXISTS schedules CASCADE;
DROP TABLE IF EXISTS medications CASCADE;

-- 1. Create the medications table, including the self-reference for history
CREATE TABLE medications (
    medication_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    previous_medication_id UUID REFERENCES medications(medication_id) ON DELETE SET NULL,
    name VARCHAR(255) NOT NULL,
    medication_type VARCHAR(50) CHECK (medication_type IN ('tablet', 'capsule', 'liquid', 'injection', 'oil', 'topical', 'other')),
    strength VARCHAR(50),
    condition_treated VARCHAR(255),
    instructions TEXT,
    amount_left NUMERIC DEFAULT 0,
    refill_threshold NUMERIC DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    treatment_duration_days INTEGER
);

-- 2. Create the schedules table, linking to medications and using a TIME array
CREATE TABLE schedules (
    schedule_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    medication_id UUID NOT NULL REFERENCES medications(medication_id) ON DELETE CASCADE,
    frequency_type VARCHAR(50) CHECK (frequency_type IN ('daily', 'weekly', 'interval', 'specific_days', 'as_needed')),
    frequency_value VARCHAR(255),
    reminder_times TIME[] 
);

-- 3. Create the dose_logs table, linking to medications and snapshotting the dose details
CREATE TABLE dose_logs (
    log_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    medication_id UUID NOT NULL REFERENCES medications(medication_id) ON DELETE CASCADE,
    scheduled_datetime TIMESTAMP WITH TIME ZONE NOT NULL,
    actual_datetime_taken TIMESTAMP WITH TIME ZONE,
    scheduled_strength VARCHAR(50),
    actual_strength_taken VARCHAR(50),
    scheduled_quantity NUMERIC DEFAULT 1,
    actual_quantity_taken NUMERIC,
    status VARCHAR(50) CHECK (status IN ('pending', 'taken', 'skipped', 'missed')) DEFAULT 'pending',
    notes TEXT
);