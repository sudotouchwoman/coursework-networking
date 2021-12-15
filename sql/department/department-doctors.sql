SELECT
    doctor.id_doctor,
    doctor.first_name,
    doctor.second_name,
    doctor.assigned_patients
FROM
    doctor
WHERE 1
    AND workplace = %s
    ORDER BY doctor.assigned_patients DESC