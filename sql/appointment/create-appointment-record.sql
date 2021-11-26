INSERT INTO appointment (
    asignee_id, patient_id,
    scheduled, about
)
VALUES(
    %s, %s,
    %s, %s)