UPDATE appointment
SET
    appointment.progress = 0,
    appointment.about = %s,
    appointment.scheduled = %s
WHERE 1
    AND appointment.id = %s