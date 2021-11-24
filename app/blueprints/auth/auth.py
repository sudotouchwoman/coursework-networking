from flask import current_app

from database.ORM import DataSource

DB_CONFIG = current_app.config['DB'].get('auth', None)
SQL_DIR = current_app.config.get('QUERIES', None)

class PolicyController:
    def __init__(self, config: dict = DB_CONFIG, sql_dir: str = SQL_DIR) -> None:
        if config is None or sql_dir is None:
            raise ValueError(f'Invalid args provided to {self.__class__.__name__}')
        self.SETTINGS = config
        self.SQL = sql_dir


    def map_credentials(self, login: str, password: str) -> str or None:

        selected = DataSource(self.SETTINGS, self.SQL).fetch_results('validate-user-credentials', login, password)
        try:
            selected = list(selected)
            selected = selected[0]
            return {
                'id': selected[0],
                'name': selected[1],
                'group': selected[2]
            }
        except (TypeError, IndexError):
            return
