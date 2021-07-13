# MathDowsers at ARQMath
Dowsing for Math Answers - the MathDowsers team's submission for ARQMath @ CLEF



### About

MathDowsers is a team of researchers from the University of  *Waterloo* who are interested in *dowsing for answers to math questions*. 

The team produces the best participant run of the Answer Retrieval task in the <a href="https://www.cs.rit.edu/~dprl/ARQMath/" target="_blank">ARQMath (**A**nswer **R**etrieval for **Q**uestions on **Math**) Lab</a> in both year 2020 and 2021; and also the best automatic run of the Formula Retrieval task in the Lab in year 2021.



### Create a document corpus for the Answer Retrieval task

The template for the document corpus is `src_2021/template_minimal_v2.html`, which is an HTML page that stores an answer together with its parent math question (that is, a question-answer pair) and other meta information. 

To create the document corpus, 


- First, download this repository followed by the Lab-provided *Math Stack Exchange* (MSE) collection at the designated paths. (Check individual README in the `data` folder)

  

- Next, navigate to the source code folder `src_2021`. Create all preprocessing files by running

  ```shell
  ./main_preprocessing.sh
  ```

  The expected files to be created are documented at each individual python file with the `prepro`-prefix .
  
- Then, demo documents can be created by running

  ```bash
  python main_generate_htmls_for_indexing.py -style minimal
  ```

  To create all documents (MSE question-answer pairs from year 2010 to year 2018)

  ```shell
  python main_generate_htmls_for_indexing.py -style minimal -year all
  ```

  The generated files will be stored at `data/ARQMath/html_minimal_2021`. See the file `main_generate_htmls_for_indexing.py` for more available options.



### Changes

*2021-07-12*: Add instructions to create the document corpus for the Answer Retrieval task.

*2021-07-04*: Initialize the repository with basic configuration.



### Bibliography

Y. K. Ng, D. J. Fraser, B. Kassaie, F. W. Tompa, Dowsing for math answers, in: CLEF 2021, volume 12880 of LNCS, 2021 (to appear)

Y. K. Ng,  D. J. Fraser,  B. Kassaie,  G. Labahn,  M. S. Marzouk,  F. W. Tompa,  K. Wang, <a href="http://ceur-ws.org/Vol-2696/paper_167.pdf" target="_blank">Dowsing for math answers with Tangent-L</a>, in: CLEF 2020, volume 2696 of CEUR Workshop Proceedings, 2020











