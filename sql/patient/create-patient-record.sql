INSERT INTO patient(
    passport, date_income,
    date_birth, firstname,
    secondname, city,
    initial_diagnosis)
    VALUES(
        %s, %s,
        %s, %s,
        %s, %s,
        %s)