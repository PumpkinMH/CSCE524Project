-- 1. Create the users table first, as other tables depend on it
CREATE TABLE users (
    user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    timezone VARCHAR(100) DEFAULT 'UTC',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 2. Create the medications table, linking to users and including the self-reference
CREATE TABLE medications (
    medication_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
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

-- 3. Create the schedules table, linking to medications and using a TIME array
CREATE TABLE schedules (
    schedule_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    medication_id UUID NOT NULL REFERENCES medications(medication_id) ON DELETE CASCADE,
    frequency_type VARCHAR(50) CHECK (frequency_type IN ('daily', 'weekly', 'interval', 'specific_days', 'as_needed')),
    frequency_value VARCHAR(255),
    reminder_times TIME[] 
);

-- 4. Create the dose_logs table, linking to medications and snapshotting the dose details
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









