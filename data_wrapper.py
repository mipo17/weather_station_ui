
import pandas as pd
import staticStrings as sss


MONTH_NAMES = {
    '01': 'Jänner', '02': 'Februar', '03': 'März', '04': 'April',
    '05': 'Mai', '06': 'Juni', '07': 'Juli', '08': 'August',
    '09': 'September', '10': 'Oktober', '11': 'November', '12': 'Dezember'
}

def get_min_max_value_per_month(conn:object, var:str, year:int):
    sql_q:str = f"""SELECT
        strftime('%m', datetime) AS month,
        AVG({var}) AS avg_temp,
        MIN({var}) AS min_temp,
        MAX({var}) AS max_temp
        FROM "{year}"
        GROUP BY month
        ORDER BY month;""" 
    
    sql_q = f"""
    WITH monthly_stats AS (
    SELECT
        strftime('%Y-%m', datetime) AS month,
        AVG({var}) AS avg_temp,
        MIN({var}) AS min_temp,
        MAX({var}) AS max_temp
        
    FROM "{year}"
    GROUP BY month
    )
    SELECT
    ms.month,
    ms.avg_temp,
    ms.min_temp,
    t_min.datetime AS min_temp_time,
    ms.max_temp,
    t_max.datetime AS max_temp_time
    FROM monthly_stats ms
    LEFT JOIN "{year}" t_min ON
    t_min.{var} = ms.min_temp AND
    strftime('%Y-%m', t_min.datetime) = ms.month
    LEFT JOIN "{year}" t_max ON
    t_max.{var} = ms.max_temp AND
    strftime('%Y-%m', t_max.datetime) = ms.month
    GROUP BY ms.month
    ORDER BY ms.month;
    """
    
    df:pd.DataFrame = conn.query(sql_q, ttl="0s")

    df['month_num'] = df['month'].str[5:7]
    
    df['month_name'] = df['month_num'].map(MONTH_NAMES)
    df['month_label'] = df['month_name']
    
    df['min_temp_time'] = pd.to_datetime(df['min_temp_time']).dt.strftime('%d.%m. %H:%M')
    df['max_temp_time'] = pd.to_datetime(df['max_temp_time']).dt.strftime('%d.%m. %H:%M')


    df_final = df[['month_label', 'min_temp', 'min_temp_time', 'max_temp', 'max_temp_time', 'avg_temp']]
    
    df_final.rename(columns={"month":"Monat", "max_temp":"Max", 
                       "min_temp":"Min", "avg_temp":"Durchschnitt",
                       "min_temp_time":"Zeitpunkt Min",
                       "max_temp_time":"Zeitpunkt Max"},inplace=True)
    return df_final


    