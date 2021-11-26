SELECT
    patient.firstname,
    patient.secondname,
    patient.initial_diagnosis, 
    patient.chamber_number,
    patient.date_income,
    patient.date_birth

    FROM patient
    WHERE 1
        AND attending_doctor = %s;