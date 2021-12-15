INSERT INTO appointment (
    assignee_id, patient_id,
    scheduled, about
)
VALUES(
    %s, %s,
    %s, %s)