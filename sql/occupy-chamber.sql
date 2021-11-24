UPDATE chamber
SET chamber.occupied = chamber.occupied + 1
WHERE 1
    AND chamber.id_chamber = %s