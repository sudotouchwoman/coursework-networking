SELECT 
    patient.id_patient,
    patient.passport,

    patient.date_income,
    patient.date_birth,

    patient.firstname,
    patient.secondname,

    patient.city,

    patient.initial_diagnosis,
    patient.outcome_diagnosis,

    patient.attending_doctor,
    patient.chamber_number,

    doctor.first_name,
    doctor.second_name
FROM
    patient JOIN doctor
    ON attending_doctor = doctor.id_doctor
WHERE 1
    AND patient.date_outcome IS NULL
    AND patient.outcome_diagnosis IS NOT NULL;
