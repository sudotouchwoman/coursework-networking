UPDATE appointment
SET appointment.progress = %s
WHERE 1
    AND appointment.id = %s