UPDATE doctor
SET
    doctor.assigned_patients = doctor.assigned_patients + 1
WHERE 1
    AND doctor.id_doctor = %s