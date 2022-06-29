import pandas

from pyplm.core import config
from pyplm.data import ATTENUATION_REMOVAL, BMP_HYDR_PERF, BMP_WQ_PERF, BMP_WQ_TYPE, EMCS, POL_MIN_CONC, PRE_BMP_LOAD
from pyplm.src.calculate_runoff import calculate_runoff

def calculate_untreated_load(vol_df, vol_col, pol):
    '''Calculates untreated pollutant load from runoff volume and landuse event mean concentration 
    ----------
    vol_df: pandas dataframe with untreated runoff volumes 
    vol_col: name of column in vol_df which contains untreated runoff volumes  
    pol: name of pollutant for which to calculate load
    '''
    emcs = EMCS()
    pol_emcs = emcs.transpose()[[pol]]
    load = (vol_df.reset_index()
             .join(pol_emcs, on = 'Land Use')
             .assign(Load = lambda df: df[vol_col]*df[pol]*28.317/453592.37)
             .set_index(['HUC','Land Use'])
             .rename(columns = {'Load':pol + ' Untreated Load'})
             [[pol + ' Untreated Load']]
            )
    return load


def calculate_attenuated_load(load_df, load_col, pol):
    '''Calculates attenuated pollutant load from non-attenuated pollutant load and subbasin attenuation percent removal
    ----------
    load_df: pandas dataframe with non-attenuated pollutant loads 
    load_col: name of column in load_df which contains non-attenuated pollutant loads
    pol: name of pollutant for which to calculate attenuated load
    '''
    attenuation_removal = ATTENUATION_REMOVAL()
    pol_removal = attenuation_removal[[pol]]
    load = (load_df
             .reset_index()
             .join(pol_removal, on = 'HUC')
             .assign(Load = lambda df: df[pol+' '+load_col]*(1-df[pol]))
             .set_index(['HUC','Land Use'])
             .rename(columns = {'Load':pol+' Attenuated Load'})
             [[pol+' Attenuated Load']]
            )
    return load 


def calculate_pre_bmp_load():
    '''Calculates untreated, attenuated load for each landuse in each subbasin
    ---------
    update: boolean indicates whether calculations should be updated, default is to not update (read from file)
    '''
    #Calculate non-attenuated pre-bmp load
    runoff = calculate_runoff()
    pre_bmp_load_no_att = runoff[['Runoff']]

    for pol in config.POLLUTANTS:
        _pre_bmp_load_no_att = calculate_untreated_load(runoff, 'Runoff', pol)
        pre_bmp_load_no_att = pre_bmp_load_no_att.join(_pre_bmp_load_no_att)

    #Calculate attenuated pre-bmp load
    pre_bmp_load = pre_bmp_load_no_att[['Runoff']]
    for pol in config.POLLUTANTS:
        _pre_bmp_load = calculate_attenuated_load(pre_bmp_load_no_att, 'Untreated Load', pol)
        pre_bmp_load = pre_bmp_load.join(_pre_bmp_load)

    return pre_bmp_load


def calculate_bmp_load(ui_subbasins, ui_bmps):
    '''Calculates non-attenuated pollutant load from BMPs based on user input
    ----------
    ui_subbasins: list of three-digit HUC subbasin IDs
    ui_bmps: pandas dataframe containing bmp implementation percentages by land use type
    '''
    runoff = calculate_runoff()
    total_bmp_load = runoff[['Runoff']].reset_index() #Create dataframe to track overall load from BMPs
    total_bmp_load['Effluent Volume'] = 0
    total_bmp_load['Volume Reduction'] = 0

    pol_flag = 1 #Use pol_flag to prevent repeating volume calcs (effluent volume and volume reduction) for all pollutants

    for pol in config.POLLUTANTS: #Iterate through pollutants
        total_bmp_load[pol+' Effluent Load'] = 0
        
        for bmp in config.BMPS: #Iterate through BMPs
                                             
            for i, subcatch in total_bmp_load.iterrows(): #Iterate through model subcatchments (subbasin + land use)
                subbasin = subcatch['HUC']

                if subbasin in ui_subbasins: #If subbasin selected by user, continue with calcs 
                    lu = subcatch['Land Use']
                    total_percent_implemented = ui_bmps.loc[lu].sum() 

                    if total_percent_implemented > 0: #If any BMPs relevant to land use are implemented, continue with calcs
                        bmp_percent_implemented = ui_bmps.loc[lu][bmp]/100

                        if bmp_percent_implemented > 0: #If BMP relevant to land use, continue with calcs
                            volume_to_bmp = subcatch['Runoff']*bmp_percent_implemented
                            capture_efficiency = BMP_HYDR_PERF().loc[bmp]['Percent Capture']
                            retention_efficiency = BMP_HYDR_PERF().loc[bmp]['Percent Reduction']
                            captured_volume = volume_to_bmp*capture_efficiency
                            volume_retained = captured_volume*retention_efficiency 
                            effluent_volume = captured_volume-volume_retained

                            if pol_flag == 1:
                                prev_effluent_volume = total_bmp_load.loc[i,'Effluent Volume']
                                total_bmp_load.loc[i,'Effluent Volume'] = prev_effluent_volume + effluent_volume
                                prev_volume_reduction = total_bmp_load.loc[i,'Volume Reduction']
                                total_bmp_load.loc[i,'Volume Reduction'] = prev_volume_reduction + volume_retained
                            
                            bmp_pol_performance = BMP_WQ_PERF().loc[bmp][pol]
                            influent_wq = EMCS().loc[pol][lu]
                            
                            if bmp_pol_performance > 0: #If BMP relevant to pollutant, continue with calcs
                                min_wq = POL_MIN_CONC().loc[pol]['Minimum Concentration']
                                
                                if influent_wq > min_wq: #If influent conc. higher than minimum, continue with calcs
                                    bmp_performance_type = BMP_WQ_TYPE().loc[bmp][pol]
                                    
                                    if bmp_performance_type == 'PR':
                                        if influent_wq*(1-bmp_pol_performance) > min_wq:
                                            effluent_wq = influent_wq*(1-bmp_pol_performance)
                                        else:
                                            effluent_wq = min_wq
                                    
                                    if bmp_performance_type == 'EQ':
                                        if bmp_pol_performance < influent_wq:
                                            effluent_wq = bmp_pol_performance
                                        else: 
                                            effluent_wq = influent_wq
                                    
                                    effluent_load = effluent_wq*effluent_volume*28.317/453592.37
                                else:
                                    effluent_load = influent_wq*effluent_volume*28.317/453592.37
                            
                            else:
                                effluent_load = influent_wq*effluent_volume*28.317/453592.37

                            prev_effluent_load = total_bmp_load.loc[i,pol+' Effluent Load']
                            total_bmp_load.loc[i,pol+' Effluent Load'] = prev_effluent_load + effluent_load

        pol_flag = 0
        
    total_bmp_load = total_bmp_load.set_index(['HUC','Land Use'])  
    total_bmp_load.to_csv('Total_BMP_Load.csv')

    return total_bmp_load  


def calculate_post_bmp_load(ui_subbasins, ui_bmps):
    '''Calculates total, attenuated load (both treated and untreated) from each land use in each subbasin
    ----------
    total_bmp_load: pandas dataframe with both untreated volume and treated load
    '''
    total_bmp_load = calculate_bmp_load(ui_subbasins, ui_bmps)
    post_bmp_load_no_att = total_bmp_load[['Runoff','Effluent Volume','Volume Reduction']]
    post_bmp_load_no_att['Untreated Volume'] = (post_bmp_load_no_att['Runoff'] 
                                        - post_bmp_load_no_att['Effluent Volume'] 
                                        - post_bmp_load_no_att['Volume Reduction']
                                        )

    # Calculate non-attenuated post-bmp load
    for pol in config.POLLUTANTS:
        _untreated_load_no_att = calculate_untreated_load(post_bmp_load_no_att, 'Untreated Volume', pol)
        _treated_load_no_att = total_bmp_load[[pol+' Effluent Load']]
        _post_bmp_load_no_att = _untreated_load_no_att.join(_treated_load_no_att)
        _post_bmp_load_no_att[pol+' Load'] = (_post_bmp_load_no_att[pol+' Untreated Load'] + 
                                            _treated_load_no_att[pol+' Effluent Load'])
        post_bmp_load_no_att = post_bmp_load_no_att.join(_post_bmp_load_no_att[pol+' Load'])
    
    #Calculate attenuated post-bmp load
    post_bmp_load = post_bmp_load_no_att[['Runoff','Effluent Volume','Volume Reduction','Untreated Volume']]
    for pol in config.POLLUTANTS:
        _post_bmp_load = calculate_attenuated_load(post_bmp_load_no_att, 'Load', pol)
        post_bmp_load = post_bmp_load.join(_post_bmp_load)

    return post_bmp_load 


def calculate_load_reduction(pre_bmp_load, post_bmp_load):
    '''Calculates load reduction by land use and subbasin acheieved by user-input bmps
    ----------
    pre_bmp_load: pandas dataframe with attenuated pre-bmp loads by pollutant 
    post_bmp_load: pandas dataframe with attenuated post-bmp loads by pollutant
    '''
    load_reduction = (pre_bmp_load.drop(['Runoff'], axis = 1) 
                  - post_bmp_load.drop(['Runoff','Effluent Volume','Volume Reduction','Untreated Volume'], axis = 1)
                 )
    return load_reduction


def calculate_percent_reduction(pre_bmp_load, load_reduction):
    '''Calculates load reduction acheived by user-input bmps as a percent of pre-bmp loads
    ----------
    pre_bmp_load: pandas dataframe with attenuated pre-bmp loads by pollutant 
    load_reduction: pandas dataframe with load reduction acheived by user-input bmps
    '''
    percent_reduction = load_reduction / pre_bmp_load.drop(['Runoff'], axis = 1) * 100
    return percent_reduction


