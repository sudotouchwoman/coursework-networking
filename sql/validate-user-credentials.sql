SELECT users.user_id, users.user_name, roles.role_name
FROM users JOIN roles on users.user_role = roles.role_id
WHERE 1
    AND users.user_login LIKE %s
    AND users.user_password LIKE %s;