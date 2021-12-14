SELECT
    doctor.id_doctor,
    doctor.first_name,
    doctor.second_name
FROM doctor
WHERE 1
    AND doctor.date_discharge IS NOT NULL