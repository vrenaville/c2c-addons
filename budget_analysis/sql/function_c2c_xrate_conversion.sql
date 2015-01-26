DROP FUNCTION IF EXISTS c2c_xrate_conversion(
    currency_id_base integer,
    currency_id_dest integer,
    value_base double precision,
    conversion_date date,
    OUT xrate numeric,
    OUT value_dest double precision)
CASCADE;

CREATE OR REPLACE FUNCTION c2c_xrate_conversion(IN currency_id_base integer, 
                                                IN currency_id_dest integer,
                                                IN value_base double precision,
                                                IN conversion_date date, 
                                                OUT xrate numeric,
                                                OUT value_dest double precision)
  RETURNS record AS
$BODY$

            DECLARE
                rcur RECORD; -- DB cursor to handle the result
                xrate_base numeric := 1;
                xrate_dest numeric := 1;

            BEGIN
            -- The exchange rate is a ratio between source currency rate and
            -- destination currency rate, not necessarily at the same date
            -- This way of calculation makes the function independent from
            -- the company currency, as we don't obviously know it here

            -- if destination currency and source currency are the same,
            -- just take the input values as it
            if currency_id_base = currency_id_dest
            then
                xrate := 1;
                value_dest := value_base;
            else
                -- read the last rate for source currency
                FOR rcur IN SELECT rate FROM res_currency_rate
                WHERE currency_id=currency_id_base
                AND name <= conversion_date ORDER BY name DESC LIMIT 1 LOOP
                    xrate_base = rcur.rate;
                END LOOP;

                -- read the last rate for destination currency
                FOR rcur IN SELECT rate FROM res_currency_rate
                WHERE currency_id=currency_id_dest
                AND name <= conversion_date ORDER BY name DESC LIMIT 1 LOOP
                    xrate_dest = rcur.rate;
                END LOOP;

                -- if an erroneous value of 0 is set, we arbitrary set the xrate to 1
                if xrate_base = 0
		        then
	                xrate = 1;
    	        else
	                xrate:= xrate_dest / xrate_base;
	        	end if;
		
                value_dest := value_base * xrate;

            end if;

            END;
            $BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
