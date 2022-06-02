select
    Date, Name, Price
from
    prices
where
    Date
between
    {start_date}
and
    {end_date}
