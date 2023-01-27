
task1_2022: prepro_2022 data-extracted

prepro_2022: data/ARQMath/prepro_2022/question2title_latex2slt.json.gz

data/ARQMath/prepro_2022/question2title_latex2slt.json.gz: src_2022/prepro*.py
	sh src_2022/main_preprocessor.sh

data-extracted: \
 data/ARQMath/data-extracted/task1_2022_data_2010.xml.gz \
 data/ARQMath/data-extracted/task1_2022_data_2011.xml.gz \
 data/ARQMath/data-extracted/task1_2022_data_2012.xml.gz \
 data/ARQMath/data-extracted/task1_2022_data_2013.xml.gz \
 data/ARQMath/data-extracted/task1_2022_data_2014.xml.gz \
 data/ARQMath/data-extracted/task1_2022_data_2015.xml.gz \
 data/ARQMath/data-extracted/task1_2022_data_2016.xml.gz \
 data/ARQMath/data-extracted/task1_2022_data_2017.xml.gz \
 data/ARQMath/data-extracted/task1_2022_data_2018.xml.gz

data/ARQMath/data-extracted/task1_2022_data_%.xml.gz: src_2022/main_generate_document_corpus.py
	cd src_2022; python3 main_generate_document_corpus.py --style minimal --year $* --output_folder ../data/ARQMath/data-extracted/ --trecdoc

