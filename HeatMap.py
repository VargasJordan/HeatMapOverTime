#create heat map over time of solar growth in San Diego

import pandas as pd
import pyodbc
import folium
from folium import plugins
from folium.plugins import HeatMap

#paramaters
start_year = 1999
end_year = 2018
out_file_name = 'SolarOverTime.html'
dot_size = 1
color_gradient = {
        0.2 : 'yellow', 
        0.5: 'orange', 
        0.8: 'red'
}

def main():
    years = [i for i in range(start_year,end_year+1)]
    d={}
    
    #SQL connections
    cs = r'DSN=ed2d;Trusted_Connection=True;'
    cnxn = pyodbc.connect(cs)
    
    #get data
    for year in years:
        qry =   """
                    SELECT
                        year=%s,
                        prm.id_latitude lat,
                        prm.id_longitude long,
                        sum(cga.app_sys_size_kw) capacity
                    FROM
                        ed2tcga_cust_gen_app cga
                    INNER JOIN
                        ed2tprm_premise prm
                        on prm.prem_id = cga.prem_id
                    WHERE
                        current_app_status_desc = 'APPROVED'
                        and gen_type_code = 'PV'       
                        and year(cga.app_approved_date) <= %s
                    GROUP BY
                        year(cga.app_approved_date),
                        prm.id_latitude,
                        prm.id_longitude
                """ % (year, year)
        df_temp = pd.read_sql_query(qry, cnxn)
        d[year] = df_temp
    
    df = pd.concat(d.values(), ignore_index=True).dropna()
    
    year_index = df.year.unique().tolist()
    
    #format data for folium
    heat_data = [[[row['lat'],row['long']]
                    for index, row in df[df['year'] == i].iterrows()]
                    for i in range(start_year,end_year+1)]

    #create map
    mp = folium.Map(location=[32.89, -117], zoom_start=10)

    hm = plugins.HeatMapWithTime(heat_data,auto_play=True,
                                 max_opacity=0.9,
                                 min_opacity=0.2,
                                 radius = dot_size,
                                 index=year_index,
                                 gradient=color_gradient)
    #save map
    hm.add_to(mp)
    mp.save(out_file_name)

if __name__ == '__main__':
    main()





