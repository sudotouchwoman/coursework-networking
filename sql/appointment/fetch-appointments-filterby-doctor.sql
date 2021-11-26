SELECT * FROM appointment
WHERE 1
    AND appointment.asignee_id = %s;