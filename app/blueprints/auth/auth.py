from app.database.ORM import DataSource
from flask import current_app

DB_CONFIG = current_app.config['DB'].get('auth', None)
SQL_DIR = current_app.config.get('QUERIES', None)

class PolicyController:
    def __init__(self, config: dict, sql_dir: str) -> None:
        if config is None or sql_dir is None: raise ValueError
        self.SETTINGS = config
        self.SQL = sql_dir

    def get_group_name(self, login:str, password:str):
        
        selected = DataSource(self.SETTINGS, self.SQL).fetch_results('select-group-names', login, password)
        if selected is None: return None
        selected = list(selected)
        if len(selected) == 0: return None
        return selected[0][0]

GLOBAL_ROLE_CONTROLLER = PolicyController(DB_CONFIG, SQL_DIR)