## The big 5 personalities
#### Description
In this repository I explore the dataset provided by kaggle https://www.kaggle.com/tunguz/big-five-personality-test . <br>
Most of the data analysis, and the steps I followed can be found in the Main.ipynb file. A lot of the code is found in the
helper_functions.py.

#### Motivation

Personality tests are very common, and there are tons of information contained in it. In this repository I aim to answer the following questions:
- Do personality scores differ for each country? Or, do they average around the same?
- Does one personality score similiar to another personality? ie: If I am an extrovert, am I also Neurotic?
- Is time a significant factor in my personality?

These are the questions that I aim to answer, with the first being the one that provoked me the most.


#### Libraries

python = 3.7.3 <br>
pandas = 1.0.2 <br>
geopandas = 0.6.1 <br>
numpy = 1.18.1 <br>
matplotlib = 3.1.3 <br>
bokeh = 2.0.0 <br>
country-converter = 0.6.7 <br> 
seaborn = 0.10.0 <br>

#### Files

- Main.ipynb : Jupyter Notebook with all the analysis included
- big-five-personality-test.pdf : Document with details of how to compute psychometric scores
- codebook.txt : Provided by the Kaggle post, contains information on each column of the data
- country_averages.csv : Computed during the analysis, contains the average psychometrics scores for each country
- helper_functions.py : Functions used during analysis
- qcodes.csv : Reference table to be used to clarify which questions refer to which columns, useful in computing psychometrics scores
- question_codes.txt : The questions in the survey with their accompanying column name
- question_list.txt : The list of the questions, numbered in their according order

#### Results

- Countries average differently in psychometric scores
- Some personalities are mildly correlated with one another
- The time taken to complete the test is not a significant factor in identifying a personality



