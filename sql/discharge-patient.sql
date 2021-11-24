UPDATE patient
    SET patient.date_outcome = %s
WHERE 1
    AND patient.id_patient = %s