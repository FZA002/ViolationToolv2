Features to add:
    More Options:
        Data for a city
        Include only un/corrected deficiencies
    
    Filter by category
    Fine per tag
    Fix annoying warning for
        new['survey_date'] = new['survey_date'].dt.strftime('%Y-%m-%d') and
        df['survey_date'] =  pd.to_datetime(df['survey_date'], format='%Y-%m-%d')
        in get_in_range


    