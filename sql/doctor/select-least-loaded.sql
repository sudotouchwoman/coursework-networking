SELECT
    doctor.id_doctor,
    doctor.first_name,
    doctor.second_name
FROM doctor
WHERE 1
    AND workplace = %s
ORDER BY assigned_patients ASC LIMIT 1