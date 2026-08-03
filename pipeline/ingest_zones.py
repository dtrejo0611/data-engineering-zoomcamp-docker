#!/usr/bin/env python
# coding: utf-8

import pandas as pd
from sqlalchemy import create_engine
from tqdm.auto import tqdm
import click

dtype = { 
    "LocationID": "Int64",
    "Borough": "string",
    "Zone": "string",
    "service_zone": "string"
}


@click.command()
@click.option('--pg-user', default='root', show_default=True, help='Postgres user')
@click.option('--pg-password', default='root', show_default=True, help='Postgres password')
@click.option('--pg-host', default='localhost', show_default=True, help='Postgres host')
@click.option('--pg-port', default=5432, show_default=True, type=int, help='Postgres port')
@click.option('--pg-db', default='ny_taxi', show_default=True, help='Postgres database')
@click.option('--table-name', default='yellow_taxi_data', show_default=True, help='Target table name')
@click.option('--chunk-size', default=100000, show_default=True, type=int, help='Chunk size for CSV iterator')
def run(pg_user, pg_password, pg_host, pg_port, pg_db, table_name, chunk_size):

    prefix = 'https://github.com/DataTalksClub/nyc-tlc-data/releases/download/misc/'
    url = f'{prefix}taxi_zone_lookup.csv'
    engine = create_engine(f'postgresql+psycopg://{pg_user}:{pg_password}@{pg_host}:{pg_port}/{pg_db}')

    df_iter = pd.read_csv(
        url,
        dtype=dtype,
        iterator=True,
        chunksize=chunk_size,
    )

    first = True

    for df_chunk in tqdm(df_iter):
        if first:
            df_chunk.head(0).to_sql(name=table_name, con=engine, if_exists='replace')
            first = False
        df_chunk.to_sql(name=table_name, con=engine, if_exists='append')

if __name__ == "__main__":
    run()