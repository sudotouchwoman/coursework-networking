UPDATE patient
SET
    patient.attending_doctor = %s,
    patient.chamber_number = %s
WHERE 1
    AND patient.id_patient = %s