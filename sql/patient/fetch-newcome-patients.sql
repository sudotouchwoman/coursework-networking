SELECT 
    patient.id_patient,
    patient.passport,
    patient.date_income,
    patient.date_birth,
    patient.firstname,
    patient.secondname,
    patient.city,
    patient.initial_diagnosis
FROM
    patient
WHERE 1
    AND patient.attending_doctor IS NULL;