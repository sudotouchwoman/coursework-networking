SELECT
    COUNT(patient.id_patient),
    doctor.first_name,
    doctor.second_name,
    doctor.assigned_patients
FROM patient LEFT JOIN doctor
on attending_doctor = doctor.id_doctor
WHERE 1
    AND date_outcome IS NULL
    AND outcome_diagnosis IS NULL
GROUP BY attending_doctor;

SELECT * FROM doctor;

SELECT
    patient.id_patient,
    patient.firstname,
    patient.secondname,
    patient.initial_diagnosis,
    patient.outcome_diagnosis,
    patient.date_outcome,
    doctor.first_name,
    doctor.second_name,
    patient.chamber_number
FROM patient JOIN doctor
ON attending_doctor = doctor.id_doctor
WHERE 1;

SELECT * FROM patient;
SELECT * from chamber;

SELECT
    COUNT(patient.chamber_number),
    chamber.id_chamber,
    chamber.department,
    chamber.totalspace,
    chamber.occupied
FROM patient JOIN chamber
on chamber_number = chamber.id_chamber
WHERE 1
    AND patient.outcome_diagnosis is NULL
    AND patient.date_outcome is NULL
GROUP BY patient.chamber_number;

SELECT * FROM department;
SELECT * FROM doctor;
SELECT * FROM chamber;
SELECT * FROM patient;
SELECT * FROM policies.users;