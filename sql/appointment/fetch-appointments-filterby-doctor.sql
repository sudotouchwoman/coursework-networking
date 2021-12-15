SELECT * FROM appointment
WHERE 1
    AND appointment.assignee_id = %s;