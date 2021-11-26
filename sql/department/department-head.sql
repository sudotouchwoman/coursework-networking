SELECT doctor.first_name, doctor.second_name
FROM department JOIN doctor
ON department.department_head = doctor.id_doctor
WHERE 1
    AND department.id_department = %s;