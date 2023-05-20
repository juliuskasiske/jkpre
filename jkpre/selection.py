import pandas as pd
import numpy as np
from plotnine import *
from jkpre import NoPandasDataException

class Redundancy:

    def check_if_pandas_df(data):
        if data.__class__.__name__ == "DataFrame" and data.__module__ == "pandas.core.frame":
            return True
        else:
            return False

    def __init__(self, data: pd.DataFrame = pd.DataFrame()) -> None:
        if Redundancy.check_if_pandas_df(data):
            self.__data = data
        else:
            raise NoPandasDataException(data)
        
        self.__continuous, self.__categorical = pd.DataFrame(), pd.DataFrame()

    @property
    def data(self) -> pd.DataFrame:
        return self.__data
    
    @data.setter
    def data(self, data: pd.DataFrame) -> None:
        if Redundancy.check_if_pandas_df(data):
            self.__data = data
        else:
            raise NoPandasDataException(data)
        
    @property
    def categorical(self) -> pd.DataFrame:
        return self.__categorical
    
    @categorical.setter
    def categorical(self, data: pd.DataFrame) -> None:
        if Redundancy.check_if_pandas_df(data):
            self.__categorical = data
        else:
            raise NoPandasDataException(data)
    
    @property
    def continuous(self) -> pd.DataFrame:
        return self.__continuous
    
    @continuous.setter
    def continuous(self, data: pd.DataFrame) -> None:
        if Redundancy.check_if_pandas_df(data):
            self.__continuous = data
        else:
            raise NoPandasDataException(data)
        
    def split_data(self, k = 10, data = None):
        """Splits DataFrames into metric and categorical tables.
        The DataFrame is split based on the number of unique
        levels in each column. Having two separate DataFrames
        is useful for analysis and visualization.

        Parameters
        ----------
        data : pandas.DataFrame
        DataFrame to be split.
        k : int, default 10
        Cutoff threshold for classifying columns as metric or continuous.

        Returns
        -------
        df_conts : pandas.DataFrame
        DataFrame with only metric variables.
        df_cats : pandas.DataFrame
        DataFrame with only categorical variables.
        """
        if not Redundancy.check_if_pandas_df(data):
            if not Redundancy.check_if_pandas_df(self.data):
                raise NoPandasDataException
            else:
                data = self.data
        
        cats = []
        for col in data:
            if pd.unique(data[col]).size <= k:
                cats.append(col)
        df_conts = data.drop(cats, axis = 1)
        df_cats = data[cats]
        self.__continuous, self.__categorical = df_conts, df_cats
        return df_conts, df_cats
    
    def correlate_continuous(self):
        df = self.continuous
        cor = df.corr(method = "spearman").round(2)
        cor["feature1"] = cor.index
        cor_melted = cor.melt(id_vars = ["feature1"], var_name = "feature2", value_name = "correlation")
        # create plot
        plot = (ggplot(cor_melted) + aes(x = "feature1", y = "feature2", fill = "correlation") + geom_tile() +
                    theme(axis_text_x = element_text(angle = 45, hjust = 1), axis_title = element_blank()) +
                    scale_fill_gradient2(midpoint=0, low="blue", mid="white", high="red") +
                    geom_text(aes(label = "correlation"), size = 6) + ggtitle("Spearman Correlation Matrix"))
        return plot
    
    def correlate(self, aggregation = "mean", midpoint = 20):
        """Calculates normalized Scaled Mean/Median Deviation
        
        This function computes a metric of association between categorical
        and continuous variables. For each categorical variable, the SMD
        with every continuous variable is computed and displayed in a 
        heatmap using geom_tile().
        
        Parameters
        ----------
        aggregation : str, default "mean"
            Aggregation function that is to be applied. Only supports
            ["mean", "median"].
        midpoint : int, default 20
            midpoint on the color gradient of the heatmap, influences 
            color differentiation.
            
        Returns
        -------
        hm_final : <ggplot: (...)>
            ggplot object with geom_tile as heatmap. The heatmap shows the
            SMD Association Matrix.
        """
        import math
        df = self.data
        df_cat = self.categorical
        df_cont = self.continuous
        # CREATE AND FILL DATA FRAME
        ## define output data frame in which to store the results, rows indeces will be the continuous features
        output_df = pd.DataFrame({"Numerical Features": df_cont.columns}).set_index("Numerical Features")
        ## loop through all categorical features
        for cat_col in df_cat:
            ### create a group by table that will be used as the iterator for the following list comprehension
            df_MS = pd.concat([df_cont, df_cat[cat_col]], axis = 1)
            df_MS_gb = df_MS.groupby(cat_col).agg(aggregation)
            ### create empty list of SMD's for each pair (i.e. list that will be the new column in the output df)
            smd_lst = []
            ### fill smd_lst
            for col in df_MS_gb:
                #### using different aggs depending on what was specified
                if aggregation == "mean":
                    f_agg = df[col].mean()
                elif aggregation == "median":
                    f_agg = df[col].median()
                #### adding a conditional constant in order to stabilize the outputs
                if abs(f_agg) >= 0.05:
                    agg_lst = [abs(df_MS_gb.loc[c_agg, col] - f_agg) / f_agg for c_agg in pd.DataFrame(df_MS_gb[col]).T]
                else:
                    f_agg = 0.05
                    agg_lst = [abs(df_MS_gb.loc[c_agg, col] - f_agg) / f_agg for c_agg in pd.DataFrame(df_MS_gb[col]).T]

                smd = sum(agg_lst)/len(agg_lst)
                smd_lst.append(smd)
            ### append that list to the data frame
            output_df[cat_col] = smd_lst

        # MELT DATA FRAME AND THEN ROUND IT
        output_df["feature1"] = output_df.T.columns
        output_df_long = output_df.melt(id_vars = ["feature1"], var_name = "feature2", value_name = "smd")
        output_df_long["smd"] = output_df_long["smd"].round(3)


        # CREATE PLOT
        ## base plot
        hm1 = ggplot(output_df_long) + aes(x = "feature1", y = "feature2", fill = "smd") + geom_tile()
        ## adjust x-axis label angle
        hm2 = hm1 + theme(axis_text_x = element_text(angle = 45, hjust = 1), 
                        axis_title = element_blank())
        ## adjust color palette
        hm3 = hm2  + scale_fill_gradient2(midpoint=midpoint, low="blue", mid="white", high="red")
        ## add labels as texts
        hm_final = hm3 + geom_text(aes(label = "smd"), size = 6) + ggtitle("SMD Association Matrix")

        return hm_final
    
    def correlate_categoricals(self, show_significance = False, alpha = 0.05, round_to = 2): 
        """Conducts Chi-squared independence test and gives p values
        
        This function performs the Chi-squared independence test for each
        pair of variables in the passed data frame. It then computes each
        test's p value and stores it in a matrix. It also measures the
        Cramers V association based on the Chi-squared statistic and thus
        gives a normalized association measure for nominal variables.
        
        Parameters
        ----------
        show_significance : bool, default False
            If True, prints matrix that shows if the p value is smaller than
            alpha. If False, prints matrix that shows cramers V which is 
            between 0 and 1.
        alpha : float, default 0.05
            Specify the significance level. Only relevant if 
            show_significance = True.
        rount_to : int, default 2
            Specify how many digits should be kept. Only relevant if
            show_significance = False.
            
        Returns
        -------
        output : <ggplot: (...)>
            ggplot object with geom_tile as heatmap. What the heatmap shows
            depends on the choice of show_significance.
        """
        
        from scipy.stats import chi2_contingency
        from scipy.stats.contingency import association
        df = self.categorical
        # define null np array with shape of target matrix and then cast it to data frame
        mt_array = np.empty(shape = (len(df.columns), len(df.columns)))
        df_cat_p = pd.DataFrame(mt_array, columns = df.columns, index = df.columns)
        df_cat_v = pd.DataFrame(mt_array, columns = df.columns, index = df.columns)
        
        # fill data frame
        for col in df:
            for row in df:
                s = chi2_contingency(pd.crosstab(df[col], df[row]))[1] # [1] for p value
                v = association(pd.crosstab(df[col], df[row])) # for cramers v
                
                df_cat_p.loc[row, col] = round(s, round_to)
                df_cat_v.loc[row, col] = round(v, round_to)
        
        # melt data frames
        df_cat_p["feature1"] = df_cat_p.index
        cat_cor_melted = df_cat_p.melt(id_vars = ["feature1"], var_name = "feature2", value_name = "correlation")
        
        df_cat_v["feature1"] = df_cat_v.index
        cat_v_melted = df_cat_v.melt(id_vars = ["feature1"], var_name = "feature2", value_name = "correlation")
        
        if show_significance:
            interm_data = (cat_cor_melted.drop(["feature2", "feature1"], axis = 1) < alpha)
            input_data = pd.concat([interm_data, cat_cor_melted["feature2"], cat_cor_melted["feature1"]], axis = 1)
        else:
            input_data = cat_v_melted

        # build plot
        hm1 = ggplot(input_data) + aes(x = "feature1", y = "feature2", fill = "correlation") + geom_tile()
        ## adjust x-axis label angle
        hm2 = hm1 + theme(axis_text_x = element_text(angle = 45, hjust = 1), 
                        axis_title = element_blank())
        ## add labels as texts
        hm_final = hm2 + geom_text(aes(label = "correlation"), size = 6)
        
        # define output
        if show_significance:
            return hm_final + scale_fill_manual(["white", "red"]) + ggtitle("P Value < 0.05, Significant Association")
        else:
            input_data = cat_cor_melted
            return (hm_final + scale_fill_gradient2(midpoint=0.5, low="white", mid="white", high="red") + 
                    ggtitle("Cramer's V Association Matrix"))
        



    




