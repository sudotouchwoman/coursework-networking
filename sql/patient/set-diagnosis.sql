UPDATE patient
    SET patient.outcome_diagnosis = %s
WHERE 1
    AND patient.id_patient = %s