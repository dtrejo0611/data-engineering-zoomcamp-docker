#!/usr/bin/env python
# coding: utf-8

import pandas as pd
from sqlalchemy import create_engine
from tqdm.auto import tqdm
import click
import pyarrow.parquet as pq

@click.command()
@click.option('--pg-user', default='root', show_default=True, help='Postgres user')
@click.option('--pg-password', default='root', show_default=True, help='Postgres password')
@click.option('--pg-host', default='localhost', show_default=True, help='Postgres host')
@click.option('--pg-port', default=5432, show_default=True, type=int, help='Postgres port')
@click.option('--pg-db', default='ny_taxi', show_default=True, help='Postgres database')
@click.option('--year', default=2021, show_default=True, type=int, help='Year of the dataset')
@click.option('--month', default=1, show_default=True, type=int, help='Month of the dataset')
@click.option('--table-name', default='yellow_taxi_data', show_default=True, help='Target table name')
@click.option('--chunk-size', default=100000, show_default=True, type=int, help='Chunk size for CSV iterator')

def run(pg_user, pg_password, pg_host, pg_port, pg_db, year, month, table_name, chunk_size):

    prefix = 'https://github.com/DataTalksClub/nyc-tlc-data/releases/download/yellow/'
    url = 'green_tripdata_2025-11.parquet'
    engine = create_engine(f'postgresql+psycopg://{pg_user}:{pg_password}@{pg_host}:{pg_port}/{pg_db}')

    # Abrir el archivo Parquet
    parquet_file = pq.ParquetFile(url)

    first = True

    # Iterar por bloques (batches)
    for batch in tqdm(parquet_file.iter_batches(batch_size=chunk_size)):
        df_chunk = batch.to_pandas()

        if first:
            # Crear la tabla con los encabezados e insertar el primer bloque
            df_chunk.head(0).to_sql(name=table_name, con=engine, if_exists='replace', index=False)
            first = False
            
        df_chunk.to_sql(name=table_name, con=engine, if_exists='append', index=False)

if __name__ == "__main__":
    run()