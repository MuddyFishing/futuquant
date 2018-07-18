from futuquant.examples.app.shock_alarm import common_parameter
from futuquant.examples.app.shock_alarm import data_process
for code in common_parameter.big_sub_codes:
    common_parameter.prev_price[code] = 0.0
data_process.quote_test(common_parameter.big_sub_codes, common_parameter.host, common_parameter.port)