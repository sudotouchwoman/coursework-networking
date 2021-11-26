SELECT * FROM appointment
WHERE 1
    AND appointment.patient_id = %s;