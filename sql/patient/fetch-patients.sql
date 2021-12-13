SELECT
    patient.id_patient,
    patient.passport,
    patient.firstname,
    patient.secondname,
    patient.date_birth,
    patient.date_income,
    patient.date_outcome,
    patient.initial_diagnosis,
    patient.outcome_diagnosis,
    patient.city,
    patient.chamber_number,
    doctor.first_name,
    doctor.second_name,
    doctor.id_doctor
FROM
    patient LEFT JOIN doctor
    ON attending_doctor = doctor.id_doctor
