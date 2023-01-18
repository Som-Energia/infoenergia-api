import asyncio 
from psycopg import AsyncConnection


class Timescale:
    CONNECTION = "postgres://{username}:{password}@{host}:{port}/{dbname}"
    
    def __init__(self, username: str, password: str, host: str, port: str, dbname: str) -> None:
        loop = asyncio.get_event_loop()

        self.db_con = loop.run_until_complete(
            AsyncConnection.connect(
                self.CONNECTION.format(
                    username=username,
                    password=password,
                    host=host,
                    port=port,
                    dbname=dbname
                )
            )
        )