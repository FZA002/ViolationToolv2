As of 6/17/22:
    Research ~Dialysis~, ~Home Health~, ~Hospice~, ~Inpatient Rehab, Long Term Care,~~ Nursing Homes~

    To get csv in pandas:
        import pandas as pd
        df = pd.read_csv("https://data.cms.gov/provider-data/api/1/datastore/query/<ID>/0/download?format=csv", encoding="iso_8859-1")

    Home health:
        Home health care:

        import pandas as pd
        hdf = pd.read_csv("https://data.cms.gov/provider-data/api/1/datastore/query/6jpm-sxkc/0/download?format=csv", encoding="iso_8859-1")

        Relevant columns:
       'state', 'provider_name', 'address'
       'city','phone', 'type_of_ownership',
       'quality_of_patient_care_star_rating',
       'footnote_for_quality_of_patient_care_star_rating',
       'how_often_the_home_health_team_began_their_patients_care_in_157c',
       'footnote_for_how_often_the_home_health_team_began_their_pat_f842',
       'how_often_the_home_health_team_taught_patients_or_their_fam_3cba',
       'footnote_for_how_often_the_home_health_team_taught_patients_bb7a',
       'how_often_the_home_health_team_determined_whether_patients__0a91',
       'footnote_for_how_often_the_home_health_team_determined_whet_035c',
       'how_often_patients_got_better_at_taking_their_drugs_correct_b296',
       'footnote_for_how_often_patients_got_better_at_taking_their__4b24',
       'how_often_physicianrecommended_actions_to_address_medicatio_7009',
       'footnote_for_how_often_physicianrecommended_actions_to_addr_8191',
       'how_much_medicare_spends_on_an_episode_of_care_at_this_agen_5868',
       'footnote_for_how_much_medicare_spends_on_an_episode_of_care_aade'

       Home health care state by state:
       import pandas as pd
       hdf = pd.read_csv("https://data.cms.gov/provider-data/api/1/datastore/query/tee5-ixt5/0/download?format=csv", encoding="iso_8859-1")

       Relevant Columns:
       'state', 'quality_of_patient_care_star_rating',
       'star_rating_1_percentage', 'star_rating_15_percentage',
       'star_rating_2_percentage', 'star_rating_25_percentage',
       'star_rating_3_percentage', 'star_rating_35_percentage',
       'star_rating_4_percentage', 'star_rating_45_percentage',
       'star_rating_5_percentage',
       'how_often_the_home_health_team_began_their_patients_care_in_157c',
       'how_often_the_home_health_team_taught_patients_or_their_fam_3cba',
       'how_often_the_home_health_team_determined_whether_patients__0a91',
       'how_often_patients_got_better_at_taking_their_drugs_correct_b296',
       'how_often_physicianrecommended_actions_to_address_medicatio_7009',
       'how_much_medicare_spends_on_an_episode_of_care_by_agencies__7b36'

       Home Health Care - Measure Date Range

       import pandas as pd
       hdf = pd.read_csv("https://data.cms.gov/provider-data/api/1/datastore/query/c886-nwpj/0/download?format=csv", encoding="iso_8859-1")

       Relevant Columns: All

    Long Term Care Hospitals:

        Long Term Care Hospitals - Provider Data:
        * Measure codes are variables related to some kind of measure for a facility. Only some are relevant.
        Relevant Measure Codes: 
            L_020_01_OBS_RATE - Percentage of patients whose medications were reviewed and who
received follow-up care when medication issues were identified

        import pandas as pd
        hdf = pd.read_csv("https://data.cms.gov/provider-data/api/1/datastore/query/fp6g-2gsn/0/download?format=csv", encoding="iso_8859-1")
        Start and end dates are for reporting period

        Relevant Columns:
        'facility_name','address_line_1',
       'address_line_2','state',
       'phone_number', 'measure_code', 'score', 'footnote',
       'start_date', 'end_date'


        Long Term Care Hospitals - General Info: 
        Only need ownership type

         import pandas as pd
         hdf = pd.read_csv("https://data.cms.gov/provider-data/api/1/datastore/query/azum-44iv/0/download?format=csv", encoding="iso_8859-1")

         Relevant columns:
         'facility_name', 'address_line_1',
       'address_line_2', 'city', 'state',
       'phone_number', 'ownership_type'
    


Current columns:
    Terr -> State -> Name -> Provider # -> City -> Addr -> Date -> Survey Type -> Deficiency Prefix -> Def Cat -> Tag -> Def Desc
    -> Def Corrected? -> Corrected Date -> Fine

       



    