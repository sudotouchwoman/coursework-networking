SELECT department.department_head as 'Head', 
SUM(chamber.totalspace) as 'Total space' 
from department JOIN chamber ON chamber.department = id_department
WHERE department.department_name like %s
GROUP BY id_department;