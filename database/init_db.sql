-- ======================
-- STAFF Table
-- ======================
CREATE TABLE STAFF (
    STAFF_ID SERIAL PRIMARY KEY,
    STAFF_FIRSTNAME VARCHAR(255),
    STAFF_LASTNAME VARCHAR(255),
    STAFF_PROF_PIC TEXT,
    STAFF_BIRTHDATE DATE,
    STAFF_ADDRESS TEXT,
    STAFF_USERNAME VARCHAR(255) NOT NULL UNIQUE,
    STAFF_PASSWORD TEXT NOT NULL
);

-- Sample data
INSERT INTO STAFF (STAFF_FIRSTNAME, STAFF_LASTNAME, STAFF_BIRTHDATE, STAFF_ADDRESS, STAFF_USERNAME, STAFF_PASSWORD)
VALUES 
('Sam Alexies', 'Dela Peña', '2005-05-05', 'Cubacub, Mandaue City', 'sam@2025', '12345'),
('Khezy Gwen', 'Mangubat', '2005-04-10', 'Tabagak, Madridejos Cebu', 'khezy@2025', '12345');


-- ======================
-- CONDITION_TYPE Table
-- ======================
CREATE TABLE CONDITION_TYPE (
    COND_ID SERIAL PRIMARY KEY,
    COND_NAME VARCHAR(50) NOT NULL
);

INSERT INTO CONDITION_TYPE (COND_NAME)
VALUES 
('First Reading'),
('Second Reading'),
('Third Reading'),
('On Hold'),
('Public Hearing'),
('Archived'),
('Approved'),
('Others');


-- ======================
-- PROPOSE_MEASURE Table
-- ======================
CREATE TABLE PROPOSE_MEASURE (
    PROPOSE_ID SERIAL PRIMARY KEY,
    PROPOSE_DATE_RCVD DATE NOT NULL,
    PROPOSE_TITLE TEXT NOT NULL,
    PROPOSE_RCVD_FROM TEXT NOT NULL,
    REMARKS TEXT,
    PROPOSE_ATTACHFILE TEXT,
    PROPOSE_RESO_NUMBER TEXT,
    PROPOSE_ORDI_NUMBER TEXT,
    PROPOSE_SESSION_DATE DATE,
    PROPOSE_AUTHOR TEXT,
    PROPOSE_IS_SCAN BOOLEAN DEFAULT FALSE,
    PROPOSE_IS_FURNISH BOOLEAN DEFAULT FALSE,
    PROPOSE_IS_PUBLICATION BOOLEAN DEFAULT FALSE,
    PROPOSE_IS_POSTING BOOLEAN DEFAULT FALSE,
    COND_ID INTEGER REFERENCES CONDITION_TYPE(COND_ID)
        ON DELETE CASCADE ON UPDATE CASCADE,
    created_by INTEGER NOT NULL REFERENCES STAFF(STAFF_ID),
    updated_by INTEGER REFERENCES STAFF(STAFF_ID),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    series_yr DATE
);


-- ======================
-- MINUTES_TYPE and MINUTES_SUBTYPE Tables
-- ======================
CREATE TABLE MINUTES_TYPE (
    TYPE_ID SERIAL PRIMARY KEY,
    TYPE_NAME VARCHAR(50) NOT NULL
);

INSERT INTO MINUTES_TYPE(TYPE_NAME)
VALUES ('Session'), ('Public Hearing'), ('Other');

CREATE TABLE MINUTES_SUBTYPE (
    SUB_ID SERIAL PRIMARY KEY,
    SUB_NAME VARCHAR(50) NOT NULL
);

INSERT INTO MINUTES_SUBTYPE(SUB_NAME)
VALUES ('Special'), ('Regular'), ('N/A');


-- ======================
-- MINUTES Table
-- ======================
CREATE TABLE MINUTES (
    MIN_ID SERIAL PRIMARY KEY,
    MIN_DATE DATE,
    MIN_LINK VARCHAR(500),
    TYPE_ID INTEGER REFERENCES MINUTES_TYPE(TYPE_ID) ON DELETE CASCADE ON UPDATE CASCADE,
    SUB_ID INTEGER REFERENCES MINUTES_SUBTYPE(SUB_ID) ON DELETE CASCADE ON UPDATE CASCADE,
    created_by INTEGER NOT NULL REFERENCES STAFF(STAFF_ID),
    updated_by INTEGER REFERENCES STAFF(STAFF_ID),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    min_series_yr DATE,
    min_num TEXT
);


-- ======================
-- COMMUNICATION_DOC Table
-- ======================
CREATE TABLE COMMUNICATION_DOC (
    COMM_ID SERIAL PRIMARY KEY,
    COMM_DATE_RCVD DATE NOT NULL,
    COMM_TITLE TEXT NOT NULL,
    COMM_VENUE TEXT,
    COMM_REMARKS TEXT,
    COMM_ATTACHFILE TEXT,
    COMM_IS_LIQUIDATE BOOLEAN DEFAULT FALSE,
    created_by INTEGER NOT NULL REFERENCES STAFF(STAFF_ID) ON DELETE CASCADE ON UPDATE CASCADE,
    updated_by INTEGER REFERENCES STAFF(STAFF_ID) ON DELETE CASCADE ON UPDATE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- ======================
-- OTHER_DOC Table
-- ======================
CREATE TABLE OTHER_DOC (
    OTHER_ID SERIAL PRIMARY KEY,
    OTHER_DATE DATE NOT NULL,
    OTHER_TITLE TEXT NOT NULL,
    OTHER_FROM TEXT,
    OTHER_STATUS TEXT,
    OTHER_ATTACHFILE TEXT,
    created_by INTEGER NOT NULL REFERENCES STAFF(STAFF_ID) ON DELETE CASCADE ON UPDATE CASCADE,
    updated_by INTEGER REFERENCES STAFF(STAFF_ID) ON DELETE CASCADE ON UPDATE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- ======================
-- HISTORY Table
-- Tracks changes across multiple tables via triggers
-- ======================
CREATE TABLE HISTORY (
    HISTORY_ID SERIAL PRIMARY KEY,
    TABLE_NAME VARCHAR(50) NOT NULL,
    ROW_TITLE TEXT NOT NULL,
    STAFF_ID INTEGER REFERENCES STAFF(STAFF_ID) ON DELETE SET NULL ON UPDATE CASCADE,
    ACTION_DETAIL TEXT NOT NULL,
    ACTION_DATE TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- ======================
-- TRASH_BIN Table
-- Stores deleted records for potential restore
-- ======================
CREATE TABLE trash_bin (
    trash_id SERIAL PRIMARY KEY,
    table_name TEXT NOT NULL,
    record_id INTEGER NOT NULL,
    deleted_data JSONB NOT NULL,
    deleted_by INTEGER REFERENCES STAFF(STAFF_ID) ON DELETE SET NULL,
    deleted_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_trash_bin_deleted_at ON trash_bin(deleted_at);


-- ======================
-- MOTIVATION_BOARD Table
-- ======================
CREATE TABLE motivation_board (
    motivation_id SERIAL PRIMARY KEY,
    motivation_text TEXT NOT NULL,
    last_updated_by INTEGER REFERENCES STAFF(STAFF_ID) ON DELETE SET NULL,
    last_updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- ======================
-- USER_ACCOMPLISHMENTS Table
-- ======================
CREATE TABLE user_accomplishments (
    accomplishment_id SERIAL PRIMARY KEY,
    staff_id INTEGER REFERENCES STAFF(STAFF_ID) ON DELETE CASCADE,
    accomplishment_text TEXT NOT NULL,
    is_completed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- ======================
-- TRIGGERS AND FUNCTIONS
-- ======================

-- Propose Measure history logging
CREATE OR REPLACE FUNCTION log_propose_measure_changes()
RETURNS TRIGGER AS $$
DECLARE
    action_text TEXT;
    changes TEXT := '';
BEGIN
    IF TG_OP = 'INSERT' THEN
        action_text := 'Created propose measure: ' || NEW.PROPOSE_TITLE;
    ELSIF TG_OP = 'UPDATE' THEN
        action_text := 'Updated propose measure: ' || NEW.PROPOSE_TITLE;
        IF NEW.PROPOSE_TITLE <> OLD.PROPOSE_TITLE THEN
            changes := changes || 'Title changed from "' || OLD.PROPOSE_TITLE || '" to "' || NEW.PROPOSE_TITLE || '". ';
        END IF;
        IF NEW.COND_ID <> OLD.COND_ID THEN
            SELECT 'Status changed from ' || old_cond.COND_NAME || ' to ' || new_cond.COND_NAME || '. '
            INTO changes
            FROM CONDITION_TYPE old_cond, CONDITION_TYPE new_cond
            WHERE old_cond.COND_ID = OLD.COND_ID AND new_cond.COND_ID = NEW.COND_ID;
        END IF;
        IF changes <> '' THEN
            action_text := action_text || ' Changes: ' || changes;
        END IF;
    ELSIF TG_OP = 'DELETE' THEN
        action_text := 'Deleted propose measure: ' || OLD.PROPOSE_TITLE;
    END IF;
    INSERT INTO HISTORY (TABLE_NAME, ROW_TITLE, STAFF_ID, ACTION_DETAIL)
    VALUES (
        'PROPOSE_MEASURE', 
        COALESCE(NEW.PROPOSE_TITLE, OLD.PROPOSE_TITLE), 
        COALESCE(NEW.updated_by, OLD.updated_by, NEW.created_by, OLD.created_by), 
        action_text
    );
    RETURN CASE WHEN TG_OP = 'DELETE' THEN OLD ELSE NEW END;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_log_propose_measure_changes
AFTER INSERT OR UPDATE OR DELETE ON PROPOSE_MEASURE
FOR EACH ROW EXECUTE FUNCTION log_propose_measure_changes();


-- Minutes history logging
CREATE OR REPLACE FUNCTION minutes_history()
RETURNS TRIGGER AS $$
DECLARE
    action_type TEXT;
    row_title TEXT;
BEGIN
    IF TG_OP = 'INSERT' THEN
        action_type := 'Created';
        row_title := NEW.min_num;
    ELSIF TG_OP = 'UPDATE' THEN
        action_type := 'Updated';
        row_title := NEW.min_num;
    ELSIF TG_OP = 'DELETE' THEN
        action_type := 'Deleted';
        row_title := OLD.min_num;
    END IF;

    INSERT INTO history(table_name, row_title, staff_id, action_detail, action_date)
    VALUES (
        'MINUTES',
        row_title,
        COALESCE(NEW.updated_by, OLD.updated_by, NEW.created_by),  -- ✅ Updated here
        action_type || ' minutes record: ' || COALESCE(row_title, 'No Title'),
        CURRENT_TIMESTAMP
    );

    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_minutes_history
AFTER INSERT OR UPDATE OR DELETE ON MINUTES
FOR EACH ROW EXECUTE FUNCTION minutes_history();


-- Other Doc history logging
CREATE OR REPLACE FUNCTION other_doc_history()
RETURNS TRIGGER AS $$
DECLARE
    action_type TEXT;
    row_title TEXT;
BEGIN
    IF TG_OP = 'INSERT' THEN
        action_type := 'Created';
        row_title := NEW.other_title;
    ELSIF TG_OP = 'UPDATE' THEN
        action_type := 'Updated';
        row_title := NEW.other_title;
    ELSIF TG_OP = 'DELETE' THEN
        action_type := 'Deleted';
        row_title := OLD.other_title;
    END IF;

    INSERT INTO history(table_name, row_title, staff_id, action_detail, action_date)
    VALUES (
        'OTHER_DOC',
        row_title,
        COALESCE(NEW.updated_by, OLD.updated_by, NEW.created_by),  -- ✅ Updated here
        action_type || ' other document: ' || COALESCE(row_title, 'No Title'),
        CURRENT_TIMESTAMP
    );

    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_other_doc_history
AFTER INSERT OR UPDATE OR DELETE ON OTHER_DOC
FOR EACH ROW EXECUTE FUNCTION other_doc_history();


-- Communication Doc history logging
CREATE OR REPLACE FUNCTION communication_doc_history()
RETURNS TRIGGER AS $$
DECLARE
    action_type TEXT;
    row_title TEXT;
BEGIN
    IF TG_OP = 'INSERT' THEN
        action_type := 'Created';
        row_title := NEW.comm_title;
    ELSIF TG_OP = 'UPDATE' THEN
        action_type := 'Updated';
        row_title := NEW.comm_title;
    ELSIF TG_OP = 'DELETE' THEN
        action_type := 'Deleted';
        row_title := OLD.comm_title;
    END IF;

    INSERT INTO history(table_name, row_title, staff_id, action_detail, action_date)
    VALUES (
        'COMMUNICATION_DOC',
        row_title,
        COALESCE(NEW.updated_by, OLD.updated_by, NEW.created_by),  -- ✅ Changed here
        action_type || ' communication document: ' || COALESCE(row_title, 'No Title'),
        CURRENT_TIMESTAMP
    );

    RETURN NULL;
END;
$$ LANGUAGE plpgsql;