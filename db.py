from pony.orm import PrimaryKey, Required, Optional, Database, commit, set_sql_debug, db_session, select

settings = dict(provider='sqlite', filename='valutes.db', create_db=True)
db = Database(**settings)
set_sql_debug(True)

class Valutes(db.Entity):
    id = PrimaryKey(int, auto=True)
    char_code = Required(str)
    date = Required(str)
    to_usd = Optional(float)
    to_eur = Optional(float)
    to_cny = Optional(float)
    to_jpy = Optional(float)


