#---------
# makefile to build indexes and run queries used in ARQMath-3.  To run things in parallel run: make -j #

task1_2022: data-indexed-2022

#--------
# PREPRO

prepro_2022: data/ARQMath/prepro_2022/question2title_latex2slt.json.gz

data/ARQMath/prepro_2022/question2title_latex2slt.json.gz: src_2022/prepro*.py
	sh src_2022/main_preprocessor.sh

#---------
# EXTRACT

data/ARQMath/data-extracted/task1_2022_data_%.xml.gz: src_2022/main_generate_document_corpus.py preproc_2022
	cd src_2022; python3 main_generate_document_corpus.py --style minimal --year $* --output_folder ../data/ARQMath/data-extracted/ --trecdoc

data/ARQMath/data-extracted/task2_2022_data.xml.gz: src_2022/extract_formulas_task2.py
	cd src_2022; python3 extract_formulas_task2.py --output_folder ../data/ARQMath/data-extracted/

#---------
# CONVERT

src_2022/mathtuples:
	cd src_2022; git clone https://github.com/fwtompa/mathtuples.git

data/ARQMath/data-extracted/task1_2022_L8_%.xml.gz: data/ARQMath/data-extracted/task1_2022_data_%.xml.gz src_2022/mathtuples src_2022/mathtuples/mathtuples/convert.py
	gunzip -c data/ARQMath/data-extracted/task1_2022_data_$(*).xml.gz | \
	  python3 src_2022/mathtuples/mathtuples/convert.py --context 2>> _convert-errors.tmp | \
	  ./src_2022/mtextsearch/mstrip.exe | \
	  gzip > data/ARQMath/data-extracted/task1_2022_L8_$(*).xml.gz

data/ARQMath/data-extracted/task2_2022_L8.xml.gz: data/ARQMath/data-extracted/task2_2022_data.xml.gz src_2022/mathtuples src_2022/mathtuples/mathtuples/convert.py
	gunzip -c data/ARQMath/data-extracted/task2_2022_data.xml.gz | \
	  python3 src_2022/mathtuples/mathtuples/convert.py --context 2>> _convert-errors.tmp | \
	  ./src_2022/mtextsearch/mstrip.exe | \
	  gzip > data/ARQMath/data-extracted/task2_2022_L8.xml.gz

#-------
# INDEX

data-indexed-2022: data/ARQMath/data-indexed/task1_2022_L8.mindex.meta data/ARQMath/data-indexed/task2_2022_L8.mindex.meta

src_2022/mtextsearch:
	cd src_2022; git clone https://github.com/andrewrkane/mtextsearch.git; cd mtextsearch; make

data/ARQMath/data-indexed/task1_2022_L8.mindex: src_2022/mtextsearch src_2022/mtextsearch/minvert.exe \
  data/ARQMath/data-extracted/task1_2022_L8_2010.xml.gz \
  data/ARQMath/data-extracted/task1_2022_L8_2018.xml.gz \
  data/ARQMath/data-extracted/task1_2022_L8_2017.xml.gz \
  data/ARQMath/data-extracted/task1_2022_L8_2016.xml.gz \
  data/ARQMath/data-extracted/task1_2022_L8_2015.xml.gz \
  data/ARQMath/data-extracted/task1_2022_L8_2014.xml.gz \
  data/ARQMath/data-extracted/task1_2022_L8_2013.xml.gz \
  data/ARQMath/data-extracted/task1_2022_L8_2012.xml.gz \
  data/ARQMath/data-extracted/task1_2022_L8_2011.xml.gz
	gunzip -c data/ARQMath/data-extracted/task1_2022_L8_*.xml.gz | \
	  src_2022/mtextsearch/minvert.exe -M > data/ARQMath/data-indexed/task1_2022_L8.mindex

data/ARQMath/data-indexed/task1_2022_L8.mindex.meta: data/ARQMath/data-indexed/task1_2022_L8.mindex src_2022/mtextsearch/mencode.exe
	src_2022/mtextsearch/mencode.exe data/ARQMath/data-indexed/task1_2022_L8.mindex


data/ARQMath/data-indexed/task2_2022_L8.mindex: src_2022/mtextsearch src_2022/mtextsearch/minvert.exe data/ARQMath/data-extracted/task2_2022_L8.xml.gz
	gunzip -c data/ARQMath/data-extracted/task1_2022_L8.xml.gz | \
	  src_2022/mtextsearch/minvert.exe -M > data/ARQMath/data-indexed/task2_2022_L8.mindex

data/ARQMath/data-indexed/task2_2022_L8.mindex.meta: data/ARQMath/data-indexed/task2_2022_L8.mindex src_2022/mtextsearch/mencode.exe
	src_2022/mtextsearch/mencode.exe data/ARQMath/data-indexed/task2_2022_L8.mindex

