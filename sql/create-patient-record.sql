INSERT INTO patient(
    passport, date_income,
    date_birth, firstname,
    secondname, city,
    attending_doctor, chamber_number)
    VALUES(
        %s, %s,
        %s, %s,
        %s, %s,
        %s, %s)