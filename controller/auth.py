from flask import current_app

from app import make_logger
from database.ORM import DataSource

DB_CONFIG = current_app.config['DB'].get('auth', None)
SQL_DIR = current_app.config.get('QUERIES', None)

class PolicyController:

    auth_log = make_logger(__name__, 'logs/auth.log')

    def __init__(self, config: dict = DB_CONFIG, sql_dir: str = SQL_DIR) -> None:
        if config is None or sql_dir is None:
            self.auth_log.fatal(msg=f'Failed to create policy controller, the args are: {DB_CONFIG}, {SQL_DIR}')
            raise ValueError(f'Invalid args provided to {self.__class__.__name__}')
        self.SOURCE = DataSource(config, sql_dir)


    def map_credentials(self, login: str, password: str) -> str or None:

        self.auth_log.debug(msg=f'Maps credentials')
        selected = self.SOURCE.fetch_results('validate-user-credentials', login, password)
        
        try:
            selected = list(selected)
            selected = selected[0]
            return {
                'id': selected[0],
                'name': selected[1],
                'group_name': selected[2],
                'group': selected[3],
            }

        except (TypeError, IndexError):
            self.auth_log.warning(msg=f'Failed to map credentials')
            return
