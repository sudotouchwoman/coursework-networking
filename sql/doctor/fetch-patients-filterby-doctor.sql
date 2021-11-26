SELECT
    patient.firstname,
    patient.secondname,
    patient.initial_diagnosis, 
    patient.outcome_diagnosis 

    FROM patient
    WHERE 1
        AND attending_doctor = %s;