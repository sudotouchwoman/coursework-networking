SELECT chamber.id_chamber FROM chamber
WHERE 1
    AND chamber.totalspace > chamber.occupied
ORDER BY totalspace DESC LIMIT 1