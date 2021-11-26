SELECT
    chamber.class,
    SUM(chamber.totalspace),
    SUM(chamber.occupied)
from chamber JOIN department ON chamber.department = department.id_department
WHERE 1
    AND department.id_department = %s
GROUP BY chamber.class;