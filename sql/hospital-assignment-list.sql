select
    patient.firstname,
    patient.secondname,
    patient.initial_diagnosis, 
    patient.outcome_diagnosis 
    from patient join doctor on attending_doctor = doctor.id_doctor 
    and doctor.second_name like %s;