
redshift_query = \
"""select   partition1 as network,
         partition2 as geo,
         partition3 as url_domain,
         partition4 as content_type,
         partition5 as size,
         partition6 as bin,
         partition7 as url_schema,
         count(*) AS bin_count,
         class,
         max(perc25_fbu)   AS perc25_fbu,
         max(perc25_dcu)   AS perc25_dcu,
         max(perc50_fbu)   AS perc50_fbu,
         max(perc50_dcu)   AS perc50_dcu,
         max(perc75_fbu)   AS perc75_fbu,
         max(perc75_dcu)   AS perc75_dcu,
         max(extra0)       AS size_25,
         max(extra1)       AS size_50,
         max(extra2)       AS size_75
FROM (
                  SELECT   network      AS partition1,
                           geo          AS partition2,
                           url_domain   AS partition3,
                           CASE
                                    WHEN content_type like '%mage%' THEN 'image'
                                    WHEN content_type like '%json%' THEN 'json'
                                    WHEN content_type like '%html%' THEN 'html'
                                    WHEN content_type like '%css%' THEN 'css'
                                    WHEN content_type like 'text/plain%' THEN 'text'
                                    WHEN content_type like '%javascript%' THEN 'javascript'
                                    WHEN content_type like 'video/%' THEN 'video'
                                    WHEN content_type like 'audio/%' THEN 'audio'
                                    WHEN content_type like '%xml%' THEN 'xml'
                                    WHEN content_type like '%binary%' THEN 'Binary File'
                                    WHEN content_type like '%octet%' THEN 'Binary File'
                                    WHEN content_type like '%font%' THEN 'Font'
                                    WHEN content_type like 'multipart%' THEN 'Multipart'
                                    WHEN content_type like 'text/%' THEN 'text'
                                    ELSE content_type
                           END AS partition4,
                           CASE
                                    WHEN size < 10000 THEN 'Small'
                                    WHEN size < 30000 THEN 'Medium'
                                    WHEN size < 50000 THEN 'Medium+'
                                    WHEN size < 200000 THEN 'Large'
                                    ELSE 'X-Large'
                           END AS partition5,
                           50*(1+floor(dcu/50)) as bin,
                           CASE
                                    WHEN dcu < 50 THEN '50'
                                    WHEN dcu < 100 THEN '100'
                                    WHEN dcu < 150 THEN '150'
                                    WHEN dcu < 200 THEN '200'
                                    WHEN dcu < 250 THEN '250'
                                    WHEN dcu < 300 THEN '300'
                                    WHEN dcu < 350 THEN '350'
                                    WHEN dcu < 400 THEN '400'
                                    WHEN dcu < 450 THEN '450'
                                    WHEN dcu < 500 THEN '500'
                                    WHEN dcu < 550 THEN '550'
                                    WHEN dcu < 600 THEN '600'
                                    WHEN dcu < 650 THEN '650'
                                    WHEN dcu < 700 THEN '700'
                                    WHEN dcu < 750 THEN '750'
                                    WHEN dcu < 800 THEN '800'
                                    WHEN dcu < 850 THEN '850'
                                    WHEN dcu < 900 THEN '900'
                                    WHEN dcu < 950 THEN '950'
                                    WHEN dcu < 1000 THEN '1000'
                                    WHEN dcu < 1050 THEN '1050'
                                    WHEN dcu < 1100 THEN '1100'
                                    WHEN dcu < 1150 THEN '1150'
                                    WHEN dcu < 1200 THEN '1200'
                                    WHEN dcu < 1250 THEN '1250'
                                    WHEN dcu < 1300 THEN '1300'
                                    WHEN dcu < 1350 THEN '1350'
                                    WHEN dcu < 1400 THEN '1400'
                                    WHEN dcu < 1450 THEN '1450'
                                    WHEN dcu < 1500 THEN '1500'
                                    WHEN dcu < 1550 THEN '1550'
                                    WHEN dcu < 1600 THEN '1600'
                                    WHEN dcu < 1650 THEN '1650'
                                    WHEN dcu < 1700 THEN '1700'
                                    WHEN dcu < 1750 THEN '1750'
                                    WHEN dcu < 1800 THEN '1800'
                                    WHEN dcu < 1850 THEN '1850'
                                    WHEN dcu < 1900 THEN '1900'
                                    WHEN dcu < 1950 THEN '1950'
                                    WHEN dcu < 2000 THEN '2000'
                                    WHEN dcu < 2050 THEN '2050'
                                    WHEN dcu < 2100 THEN '2100'
                                    WHEN dcu < 2150 THEN '2150'
                                    WHEN dcu < 2200 THEN '2200'
                                    WHEN dcu < 2250 THEN '2250'
                                    WHEN dcu < 2300 THEN '2300'
                                    WHEN dcu < 2350 THEN '2350'
                                    WHEN dcu < 2400 THEN '2400'
                                    WHEN dcu < 2450 THEN '2450'
                                    WHEN dcu < 2500 THEN '2500'
                                    WHEN dcu < 2550 THEN '2550'
                                    WHEN dcu < 2600 THEN '2600'
                                    WHEN dcu < 2650 THEN '2650'
                                    WHEN dcu < 2700 THEN '2700'
                                    WHEN dcu < 2750 THEN '2750'
                                    WHEN dcu < 2800 THEN '2800'
                                    WHEN dcu < 2850 THEN '2850'
                                    WHEN dcu < 2900 THEN '2900'
                                    WHEN dcu < 2950 THEN '2950'
                                    WHEN dcu < 3000 THEN '3000'
                                    WHEN dcu < 3050 THEN '3050'
                                    WHEN dcu < 3100 THEN '3100'
                                    WHEN dcu < 3150 THEN '3150'
                                    WHEN dcu < 3200 THEN '3200'
                                    WHEN dcu < 3250 THEN '3250'
                                    WHEN dcu < 3300 THEN '3300'
                                    WHEN dcu < 3350 THEN '3350'
                                    WHEN dcu < 3400 THEN '3400'
                                    WHEN dcu < 3450 THEN '3450'
                                    WHEN dcu < 3500 THEN '3500'
                                    WHEN dcu < 3550 THEN '3550'
                                    WHEN dcu < 3600 THEN '3600'
                                    WHEN dcu < 3650 THEN '3650'
                                    WHEN dcu < 3700 THEN '3700'
                                    WHEN dcu < 3750 THEN '3750'
                                    WHEN dcu < 3800 THEN '3800'
                                    WHEN dcu < 3850 THEN '3850'
                                    WHEN dcu < 3900 THEN '3900'
                                    WHEN dcu < 3950 THEN '3950'
                                    WHEN dcu < 4000 THEN '4000'
                                    WHEN dcu >= 4000 THEN '>4000'
                           END AS partition6,
                           url_schema as partition7,
                           class,
                           percentile_cont(0.25) within GROUP (ORDER BY size) OVER (partition BY network, geo, url_domain, content_type,
                           CASE
                                    WHEN size < 10000 THEN 'Small'
                                    WHEN size < 30000 THEN 'Medium'
                                    WHEN size < 50000 THEN 'Medium+'
                                    WHEN size < 200000 THEN 'Large'
                                    ELSE 'X-Large'
                           END,
                           CASE
                                    WHEN content_type like '%mage%' THEN 'image'
                                    WHEN content_type like '%json%' THEN 'json'
                                    WHEN content_type like '%html%' THEN 'html'
                                    WHEN content_type like '%css%' THEN 'css'
                                    WHEN content_type like 'text/plain%' THEN 'text'
                                    WHEN content_type like '%javascript%' THEN 'javascript'
                                    WHEN content_type like 'video/%' THEN 'video'
                                    WHEN content_type like 'audio/%' THEN 'audio'
                                    WHEN content_type like '%xml%' THEN 'xml'
                                    WHEN content_type like '%binary%' THEN 'Binary File'
                                    WHEN content_type like '%octet%' THEN 'Binary File'
                                    WHEN content_type like '%font%' THEN 'Font'
                                    WHEN content_type like 'multipart%' THEN 'Multipart'
                                    ELSE content_type
                           END,
                           class) AS extra0,
                           median(size) OVER (partition BY network, geo, url_domain, content_type,
                           CASE
                                    WHEN size < 10000 THEN 'Small'
                                    WHEN size < 30000 THEN 'Medium'
                                    WHEN size < 50000 THEN 'Medium+'
                                    WHEN size < 200000 THEN 'Large'
                                    ELSE 'X-Large'
                           END,
                           CASE
                                    WHEN content_type like '%mage%' THEN 'image'
                                    WHEN content_type like '%json%' THEN 'json'
                                    WHEN content_type like '%html%' THEN 'html'
                                    WHEN content_type like '%css%' THEN 'css'
                                    WHEN content_type like 'text/plain%' THEN 'text'
                                    WHEN content_type like '%javascript%' THEN 'javascript'
                                    WHEN content_type like 'video/%' THEN 'video'
                                    WHEN content_type like 'audio/%' THEN 'audio'
                                    WHEN content_type like '%xml%' THEN 'xml'
                                    WHEN content_type like '%binary%' THEN 'Binary File'
                                    WHEN content_type like '%octet%' THEN 'Binary File'
                                    WHEN content_type like '%font%' THEN 'Font'
                                    WHEN content_type like 'multipart%' THEN 'Multipart'
                                    ELSE content_type
                           END,
                           class) AS extra1,
                           percentile_cont(0.75) within GROUP (ORDER BY size) OVER (partition BY network, geo, url_domain, content_type,
                           CASE
                                    WHEN size < 10000 THEN 'Small'
                                    WHEN size < 30000 THEN 'Medium'
                                    WHEN size < 50000 THEN 'Medium+'
                                    WHEN size < 200000 THEN 'Large'
                                    ELSE 'X-Large'
                           END,
                           CASE
                                    WHEN content_type like '%mage%' THEN 'image'
                                    WHEN content_type like '%json%' THEN 'json'
                                    WHEN content_type like '%html%' THEN 'html'
                                    WHEN content_type like '%css%' THEN 'css'
                                    WHEN content_type like 'text/plain%' THEN 'text'
                                    WHEN content_type like '%javascript%' THEN 'javascript'
                                    WHEN content_type like 'video/%' THEN 'video'
                                    WHEN content_type like 'audio/%' THEN 'audio'
                                    WHEN content_type like '%xml%' THEN 'xml'
                                    WHEN content_type like '%binary%' THEN 'Binary File'
                                    WHEN content_type like '%octet%' THEN 'Binary File'
                                    WHEN content_type like '%font%' THEN 'Font'
                                    WHEN content_type like 'multipart%' THEN 'Multipart'
                                    ELSE content_type
                           END,
                           class) AS extra2,
                           percentile_cont(0.25) within GROUP (ORDER BY fbu) OVER (partition BY network, geo, url_domain, content_type,
                           CASE
                                    WHEN size < 10000 THEN 'Small'
                                    WHEN size < 30000 THEN 'Medium'
                                    WHEN size < 50000 THEN 'Medium+'
                                    WHEN size < 200000 THEN 'Large'
                                    ELSE 'X-Large'
                           END,
                           CASE
                                    WHEN content_type like '%mage%' THEN 'image'
                                    WHEN content_type like '%json%' THEN 'json'
                                    WHEN content_type like '%html%' THEN 'html'
                                    WHEN content_type like '%css%' THEN 'css'
                                    WHEN content_type like 'text/plain%' THEN 'text'
                                    WHEN content_type like '%javascript%' THEN 'javascript'
                                    WHEN content_type like 'video/%' THEN 'video'
                                    WHEN content_type like 'audio/%' THEN 'audio'
                                    WHEN content_type like '%xml%' THEN 'xml'
                                    WHEN content_type like '%binary%' THEN 'Binary File'
                                    WHEN content_type like '%octet%' THEN 'Binary File'
                                    WHEN content_type like '%font%' THEN 'Font'
                                    WHEN content_type like 'multipart%' THEN 'Multipart'
                                    ELSE content_type
                           END,
                           class) AS perc25_fbu,
                           percentile_cont(0.25) within GROUP (ORDER BY dcu) OVER (partition BY network, geo, url_domain, content_type,
                           CASE
                                    WHEN size < 10000 THEN 'Small'
                                    WHEN size < 30000 THEN 'Medium'
                                    WHEN size < 50000 THEN 'Medium+'
                                    WHEN size < 200000 THEN 'Large'
                                    ELSE 'X-Large'
                           END,
                           CASE
                                    WHEN content_type like '%mage%' THEN 'image'
                                    WHEN content_type like '%json%' THEN 'json'
                                    WHEN content_type like '%html%' THEN 'html'
                                    WHEN content_type like '%css%' THEN 'css'
                                    WHEN content_type like 'text/plain%' THEN 'text'
                                    WHEN content_type like '%javascript%' THEN 'javascript'
                                    WHEN content_type like 'video/%' THEN 'video'
                                    WHEN content_type like 'audio/%' THEN 'audio'
                                    WHEN content_type like '%xml%' THEN 'xml'
                                    WHEN content_type like '%binary%' THEN 'Binary File'
                                    WHEN content_type like '%octet%' THEN 'Binary File'
                                    WHEN content_type like '%font%' THEN 'Font'
                                    WHEN content_type like 'multipart%' THEN 'Multipart'
                                    ELSE content_type
                           END,
                           class) AS perc25_dcu,
                           median(fbu) OVER (partition BY network, geo, url_domain, content_type,
                           CASE
                                    WHEN size < 10000 THEN 'Small'
                                    WHEN size < 30000 THEN 'Medium'
                                    WHEN size < 50000 THEN 'Medium+'
                                    WHEN size < 200000 THEN 'Large'
                                    ELSE 'X-Large'
                           END,
                           CASE
                                    WHEN content_type like '%mage%' THEN 'image'
                                    WHEN content_type like '%json%' THEN 'json'
                                    WHEN content_type like '%html%' THEN 'html'
                                    WHEN content_type like '%css%' THEN 'css'
                                    WHEN content_type like 'text/plain%' THEN 'text'
                                    WHEN content_type like '%javascript%' THEN 'javascript'
                                    WHEN content_type like 'video/%' THEN 'video'
                                    WHEN content_type like 'audio/%' THEN 'audio'
                                    WHEN content_type like '%xml%' THEN 'xml'
                                    WHEN content_type like '%binary%' THEN 'Binary File'
                                    WHEN content_type like '%octet%' THEN 'Binary File'
                                    WHEN content_type like '%font%' THEN 'Font'
                                    WHEN content_type like 'multipart%' THEN 'Multipart'
                                    ELSE content_type
                           END,
                           class)  AS perc50_fbu,
                           median(dcu) OVER (partition BY network, geo, url_domain, content_type,
                           CASE
                                    WHEN size < 10000 THEN 'Small'
                                    WHEN size < 30000 THEN 'Medium'
                                    WHEN size < 50000 THEN 'Medium+'
                                    WHEN size < 200000 THEN 'Large'
                                    ELSE 'X-Large'
                           END,
                           CASE
                                    WHEN content_type like '%mage%' THEN 'image'
                                    WHEN content_type like '%json%' THEN 'json'
                                    WHEN content_type like '%html%' THEN 'html'
                                    WHEN content_type like '%css%' THEN 'css'
                                    WHEN content_type like 'text/plain%' THEN 'text'
                                    WHEN content_type like '%javascript%' THEN 'javascript'
                                    WHEN content_type like 'video/%' THEN 'video'
                                    WHEN content_type like 'audio/%' THEN 'audio'
                                    WHEN content_type like '%xml%' THEN 'xml'
                                    WHEN content_type like '%binary%' THEN 'Binary File'
                                    WHEN content_type like '%octet%' THEN 'Binary File'
                                    WHEN content_type like '%font%' THEN 'Font'
                                    WHEN content_type like 'multipart%' THEN 'Multipart'
                                    ELSE content_type
                           END,
                           class) AS perc50_dcu,
                           percentile_cont(0.75) within GROUP (ORDER BY fbu) OVER (partition BY network, geo, url_domain, content_type,
                           CASE
                                    WHEN size < 10000 THEN 'Small'
                                    WHEN size < 30000 THEN 'Medium'
                                    WHEN size < 50000 THEN 'Medium+'
                                    WHEN size < 200000 THEN 'Large'
                                    ELSE 'X-Large'
                           END,
                           CASE
                                    WHEN content_type like '%mage%' THEN 'image'
                                    WHEN content_type like '%json%' THEN 'json'
                                    WHEN content_type like '%html%' THEN 'html'
                                    WHEN content_type like '%css%' THEN 'css'
                                    WHEN content_type like 'text/plain%' THEN 'text'
                                    WHEN content_type like '%javascript%' THEN 'javascript'
                                    WHEN content_type like 'video/%' THEN 'video'
                                    WHEN content_type like 'audio/%' THEN 'audio'
                                    WHEN content_type like '%xml%' THEN 'xml'
                                    WHEN content_type like '%binary%' THEN 'Binary File'
                                    WHEN content_type like '%octet%' THEN 'Binary File'
                                    WHEN content_type like '%font%' THEN 'Font'
                                    WHEN content_type like 'multipart%' THEN 'Multipart'
                                    ELSE content_type
                           END,
                           class) AS perc75_fbu,
                           percentile_cont(0.75) within GROUP (ORDER BY dcu) OVER (partition BY network, geo, url_domain, content_type,
                           CASE
                                    WHEN size < 10000 THEN 'Small'
                                    WHEN size < 30000 THEN 'Medium'
                                    WHEN size < 50000 THEN 'Medium+'
                                    WHEN size < 200000 THEN 'Large'
                                    ELSE 'X-Large'
                           END,
                           CASE
                                    WHEN content_type like '%mage%' THEN 'image'
                                    WHEN content_type like '%json%' THEN 'json'
                                    WHEN content_type like '%html%' THEN 'html'
                                    WHEN content_type like '%css%' THEN 'css'
                                    WHEN content_type like 'text/plain%' THEN 'text'
                                    WHEN content_type like '%javascript%' THEN 'javascript'
                                    WHEN content_type like 'video/%' THEN 'video'
                                    WHEN content_type like 'audio/%' THEN 'audio'
                                    WHEN content_type like '%xml%' THEN 'xml'
                                    WHEN content_type like '%binary%' THEN 'Binary File'
                                    WHEN content_type like '%octet%' THEN 'Binary File'
                                    WHEN content_type like '%font%' THEN 'Font'
                                    WHEN content_type like 'multipart%' THEN 'Multipart'
                                    ELSE content_type
                           END,
                           class) AS perc75_dcu
                  FROM     tplog
                  WHERE    datetime > '{start_date}'
                  AND      datetime < '{end_date}'
                  AND      cid = {cid}
                  AND      network IS NOT NULL
                  AND      geo IS NOT NULL
                  AND      url_domain IS NOT NULL
                  AND      content_type IS NOT NULL
                  AND      size IS NOT NULL
                  AND      dcu IS NOT NULL ) AS nested
GROUP BY partition1,
         partition2,
         partition3,
         partition4,
         partition5,
         partition6,
         partition7,
         class
ORDER BY partition1,
         partition2,
         partition3,
         partition4,
         partition5,
         partition6
LIMIT {limit};"""

content_types = {
    '': 'none',
    'application/font-woff': 'font',
    'application/javascript': 'json',
    'application/json': 'json',
    'application/octet-stream': 'binary',
    'application/x-font-ttf': 'font',
    'application/x-font-woff': 'font',
    'application/x-javascript': 'application',
    'application/xml': 'application',
    'font/opentype': 'font',
    'font/ttf': 'font',
    'image': 'image',
    'image/gif': 'image',
    'image/jpeg': 'image',
    'image/jpg': 'image',
    'image/png': 'image',
    'image/webp': 'image',
    'image/svg+xml': 'image',
    'Image': 'image',
    'multipart': 'multipart',
    'text': 'text',
    'text/css': 'text',
    'text/html': 'text',
    'text/javascript': 'text',
    'text/plain': 'text'
    }

def parseSelector(selector_string):
    '''returns a dict of filter lists to be applied and an optional error'''
    
    selector_types = {
            ' = ': [],
            ' like ': [],
            ' in ': []
            }

    if not selector_string:
        return selector_types, None

    selectors = selector_string.split('and')
    for selector in selectors:
        select_type = [x for x in selector_types if x in selector]
        if len(select_type) != 1:
            return {}, "Selector error in {}".format(selector)
        
        s_type = select_type[0]
        split_selector = [x.strip() for x in selector.split(s_type)]
        if s_type == ' in ':
            split_selector[1] = [x.strip() for x in split_selector[1].replace(')','').replace('(','').split(',')]
        
        selector_types[s_type].append(split_selector)

    print selector_types
    
    return selector_types, None 
