SELECT
    patient.firstname,
    patient.secondname,
    patient.initial_diagnosis, 
    patient.chamber_number,
    patient.date_income,
    patient.date_birth,
    patient.date_outcome

    FROM patient
    WHERE 1
        AND attending_doctor = %s;