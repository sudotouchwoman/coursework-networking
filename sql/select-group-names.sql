SELECT roles.role_name 
FROM roles
WHERE roles.role_login like %s
AND roles.role_password like %s;