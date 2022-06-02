import re
import sqlparse
import pandas as pd
from sqlalchemy import create_engine


def dataframe_to_sql(df, table, password, db='footballindex', if_exists='append'):
    """
    :param db: Database to be updated
    :param if_exists: Method of upload
    :param df: Dataframe object to be uploaded
    :param table: Table within the SQL database
    :return: N/A
    """

    connection = create_engine(f'mysql+pymysql://root:{password}@192.168.0.46:3306/{db}').connect()

    df.to_sql(table, con=connection, if_exists=if_exists, index=False)

    connection.close()


def sql_query(sql, password, db='footballindex'):
    """
    :param sql: Query to be executed
    :param db: Database to be queried
    :return: Dataframe of output from sql
    """

    connection = create_engine(f'mysql+pymysql://root:{password}@192.168.0.46:3306/{db}').connect()

    df = pd.read_sql(sql, connection)

    connection.close()

    return df


def read_sql(sql, sql_params={}, no_quotes=[]):
    """
    Reads a sql string, removes comments, and substitutes a dict of parameters
    Parameters will be expected in the format {param}

    Where a list is passed (e.g. param = ['a','b','c'] ) this will output a quoted list (e.g. "'a','b','c'")
    This is the desired behaviour for WHERE clauses, UNNEST() etc.

    If quotes are not wanted, for example in a SELECT statement, this can be declared using the no_quotes argument
    i.e. if sql_params={'param': ['a','b','c']} & no_quotes=['param'], then '{param}' will be substituted to "a, b, c"

    :param sql: string, the SQL to be parameterised
    :param sql_params: dict, example {'param_1': 3, 'param_2': ['a','b','c']}
    :param no_quotes: list, example ['param_2']
    :return: string
    """

    if isinstance(no_quotes, str):
        no_quotes = [no_quotes]

    assert set(no_quotes) <= set(sql_params.keys()), 'no_quotes must be a subset of sql_params.keys()'

    sql = sqlparse.format(sql, strip_comments=True)

    # substitute parameters:
    for key in sql_params.keys():

        if isinstance(sql_params[key], list):
            if key in no_quotes:
                items = [str(i) for i in sql_params[key]]
            else:
                items = ['\'{}\''.format(str(i)) for i in sql_params[key]]
            parsed_param = ','.join(items)
        else:
            parsed_param = str(sql_params[key])

        sql = re.sub('{{{}}}'.format(key), parsed_param, sql)

    return sql


def read_sql_file(sql_path, sql_params={}, no_quotes=[]):
    """
    Reads a sql string from a saved file, removes comments, and substitutes a dict of parameters
    Parameters will be expected in the format {param}

    Where a list is passed (e.g. param = ['a','b','c'] ) this will output a quoted list (e.g. "'a','b','c'")
    This is the desired behaviour for WHERE clauses, UNNEST() etc.

    If quotes are not wanted, for example in a SELECT statement, this can be declared using the no_quotes argument
    i.e. if sql_params={'param': ['a','b','c']} & no_quotes=['param'], then '{param}' will be substituted to "a, b, c"

    :param sql_path: string, the (relative) path to the SQL file
    :param sql_params: dict, example {'param_1': 3, 'param_2': ['a','b','c']}
    :param no_quotes: list, example ['param_2']
    :return: string
    """

    # read the sql, remove the comments:
    with open(sql_path, 'r') as f:
        sql = f.read()

    return read_sql(sql=sql,  sql_params=sql_params, no_quotes=no_quotes)
