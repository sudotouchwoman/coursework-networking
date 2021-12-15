CREATE TABLE appointment (  
    id int NOT NULL primary key AUTO_INCREMENT COMMENT 'Primary Key',
    assignee_id INT NOT NULL COMMENT 'Doctor id',
    patient_id INT NOT NULL COMMENT 'Patient id',
    scheduled DATETIME COMMENT 'Datetime of request',
    about TEXT COMMENT 'Brief description',
    progress INT UNSIGNED DEFAULT 0 COMMENT 'Mask',
    FOREIGN KEY (assignee_id)
        REFERENCES doctor(id_doctor),
    FOREIGN KEY (patient_id)
        REFERENCES patient(id_patient)
) default charset utf8 COMMENT '';