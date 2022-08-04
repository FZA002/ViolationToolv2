import pandas as pd
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

def download_data():
    ''' Downloads data related to Home Health Care organizations and returns the dataframes to be saved
       by the main download method in utilities.py as a dictionary. '''

    # Download data for home health care for organizations and states as a csv, turn it into a dataframe
    # with only relevant columns
    hhq = pd.read_csv("https://data.cms.gov/provider-data/api/1/datastore/query/6jpm-sxkc/0/download?format=csv", encoding="iso_8859-1")
    hhq = hhq[['state', 'provider_name', 'city', 'address',
        'phone', 'type_of_ownership',
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
        'footnote_for_how_much_medicare_spends_on_an_episode_of_care_aade']]

    # Rename the columns
    hhq = hhq.rename(columns={
        'state':'provider_state',
        'city':'provider_city',
        'address':'provider_address',
        'how_often_the_home_health_team_began_their_patients_care_in_157c':
                'how_often_the_home_health_team_began_their_patients_care_in_a_timely_manner',
        'footnote_for_how_often_the_home_health_team_began_their_pat_f842':
                'footnote_for_how_often_the_home_health_team_began_their_patients_care_in_a_timely_manner',
        'how_often_the_home_health_team_taught_patients_or_their_fam_3cba':
                'how_often_the_home_health_team_taught_patients_or_their_family_about_their_drugs',
        'footnote_for_how_often_the_home_health_team_taught_patients_bb7a':
                'footnote_for_how_often_the_home_health_team_taught_patients_or_their_family_about_their_drugs',
        'how_often_the_home_health_team_determined_whether_patients__0a91':
                'how_often_the_home_health_team_determined_whether_patients_received_a_flu_shot_for_the_current_season',
        'footnote_for_how_often_the_home_health_team_determined_whet_035c':
                'footnote_for_how_often_the_home_health_team_determined_whether_patients_received_a_flu_shot_for_the_current_season',
        'how_often_patients_got_better_at_taking_their_drugs_correct_b296':
                'how_often_patients_got_better_at_taking_their_drugs_correctly_by_mouth',
        'footnote_for_how_often_patients_got_better_at_taking_their__4b24':
                'footnote_for_how_often_patients_got_better_at_taking_their_drugs_correctly_by_mouth',
        'how_often_physicianrecommended_actions_to_address_medicatio_7009':
                'how_often_physician_recommended_actions_to_address_medication_issues_were_completely_timely',
        'footnote_for_how_often_physicianrecommended_actions_to_addr_8191':
                'footnote_for_how_often_physician_recommended_actions_to_address_medication_issues_were_completely_timely',
        'how_much_medicare_spends_on_an_episode_of_care_at_this_agen_5868':
                'how_much_medicare_spends_on_an_episode_of_care_at_this_agency_compared_to_medicare_spending_across_all_agencies_nationally',
        'footnote_for_how_much_medicare_spends_on_an_episode_of_care_aade':
                'footnote_for_how_much_medicare_spends_on_an_episode_of_care_at_this_agency_compared_to_medicare_spending_across_all_agencies_nationally'})

    # Download home health care state by state data, for use as an optional excel sheet, and put it into a dataframe with
    # only relevant columns
    hhs = pd.read_csv("https://data.cms.gov/provider-data/api/1/datastore/query/tee5-ixt5/0/download?format=csv", encoding="iso_8859-1")
    hhs = hhs[['state', 'quality_of_patient_care_star_rating',
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
       'how_much_medicare_spends_on_an_episode_of_care_by_agencies__7b36']]

    # Rename the columns
    hhs = hhs.rename(columns={
        'state':'provider_state',
        'star_rating_15_percentage': 'star_rating_1.5_percentage',
        'star_rating_25_percentage':'star_rating_2.5_percentage',
        'star_rating_35_percentage':'star_rating_3.5_percentage',
        'star_rating_45_percentage':'star_rating_4.5_percentage',
        'how_often_the_home_health_team_began_their_patients_care_in_157c':
                'how_often_the_home_health_team_began_their_patients_care_in_a_timely_manner',
       'how_often_the_home_health_team_taught_patients_or_their_fam_3cba':
                'how_often_the_home_health_team_taught_patients_or_their_family_about_their_drugs',
       'how_often_the_home_health_team_determined_whether_patients__0a91':
                'how_often_the_home_health_team_determined_whether_patients_received_a_flu_shot_for_the_current_season',
       'how_often_patients_got_better_at_taking_their_drugs_correct_b296':
                'how_often_patients_got_better_at_taking_their_drugs_correctly_by_mouth',
       'how_often_physicianrecommended_actions_to_address_medicatio_7009':
                'how_often_physician_recommended_actions_to_address_medication_issues_were_completely_timely',
       'how_much_medicare_spends_on_an_episode_of_care_by_agencies__7b36':
                'how_much_medicare_spends_on_an_episode_of_care_at_this_agency_compared_to_medicare_spending_across_all_agencies_nationally'})

    # Download the date ranges for certain columns in the above dataframes
    mdr = pd.read_csv("https://data.cms.gov/provider-data/api/1/datastore/query/c886-nwpj/0/download?format=csv", encoding="iso_8859-1")

    return {"mdr":mdr, 'hhs':hhs, 'hhq':hhq}



        