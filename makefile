# makefile to build indexes and run queries used in ARQMath-3.  To run things in parallel run: make -j #

all: eval

# ------------------ PREPRO ------------------
prepro_2022: data/ARQMath/prepro_2022/question2title_latex2slt.json.gz

data/ARQMath/prepro_2022/question2title_latex2slt.json.gz: src_2022/prepro*.py
	sh src_2022/main_preprocessor.sh

# ------------------ EXTRACT ------------------
data/ARQMath/data-extracted/task1_2022_data_%.xml.gz: src_2022/main_generate_document_corpus.py preproc_2022
	cd src_2022; python3 main_generate_document_corpus.py --style minimal --year $* --output_folder ../data/ARQMath/data-extracted/ --trecdoc

data/ARQMath/data-extracted/task2_2022_data.xml.gz: src_2022/extract_formulas_task2.py
	cd src_2022; python3 extract_formulas_task2.py --output_folder ../data/ARQMath/data-extracted/

# ------------------ CONVERT ------------------
src_2022/mathtuples:
	cd src_2022; git clone https://github.com/fwtompa/mathtuples.git

data/ARQMath/data-extracted/task1_2022_L8_%.xml.gz: data/ARQMath/data-extracted/task1_2022_data_%.xml.gz src_2022/mathtuples src_2022/mathtuples/mathtuples/convert.py
	gunzip -c data/ARQMath/data-extracted/task1_2022_data_$(*).xml.gz \
	  | python3 src_2022/mathtuples/mathtuples/convert.py --context 2>> _convert-errors.tmp \
	  | ./src_2022/mtextsearch/mstrip.exe \
	  | gzip > data/ARQMath/data-extracted/task1_2022_L8_$(*).xml.gz

data/ARQMath/data-extracted/task2_2022_L8.xml.gz: data/ARQMath/data-extracted/task2_2022_data.xml.gz src_2022/mathtuples src_2022/mathtuples/mathtuples/convert.py
	gunzip -c data/ARQMath/data-extracted/task2_2022_data.xml.gz \
	  | python3 src_2022/mathtuples/mathtuples/convert.py --context 2>> _convert-errors.tmp \
	  | ./src_2022/mtextsearch/mstrip.exe \
	  | gzip > data/ARQMath/data-extracted/task2_2022_L8.xml.gz

# ------------------ INDEX ------------------
src_2022/mtextsearch:
	cd src_2022; git clone https://github.com/andrewrkane/mtextsearch.git; cd mtextsearch; make

data/ARQMath/data-indexed/task1_2022_L8.mindex: src_2022/mtextsearch src_2022/mtextsearch/minvert.exe \
  data/ARQMath/data-extracted/task1_2022_L8_2010.xml.gz data/ARQMath/data-extracted/task1_2022_L8_2018.xml.gz data/ARQMath/data-extracted/task1_2022_L8_2017.xml.gz \
  data/ARQMath/data-extracted/task1_2022_L8_2016.xml.gz data/ARQMath/data-extracted/task1_2022_L8_2015.xml.gz data/ARQMath/data-extracted/task1_2022_L8_2014.xml.gz \
  data/ARQMath/data-extracted/task1_2022_L8_2013.xml.gz data/ARQMath/data-extracted/task1_2022_L8_2012.xml.gz data/ARQMath/data-extracted/task1_2022_L8_2011.xml.gz
	gunzip -c data/ARQMath/data-extracted/task1_2022_L8_*.xml.gz \
	  | src_2022/mtextsearch/minvert.exe -M > data/ARQMath/data-indexed/task1_2022_L8.mindex

data/ARQMath/data-indexed/task1_2022_L8.mindex.meta: data/ARQMath/data-indexed/task1_2022_L8.mindex src_2022/mtextsearch/mencode.exe
	src_2022/mtextsearch/mencode.exe data/ARQMath/data-indexed/task1_2022_L8.mindex

data/ARQMath/data-indexed/task2_2022_latex_L8.mindex: src_2022/mtextsearch src_2022/mtextsearch/minvert.exe data/ARQMath/data-extracted/task2_2022_L8.xml.gz
	gunzip -c data/ARQMath/data-extracted/task2_2022_L8.xml.gz \
	  | python3 src_2022/latex_filter_stopwords.py -tsv data/ARQMath/data-original/Formulas/latex_representation_v3/ \
	  | src_2022/mtextsearch/minvert.exe -M > data/ARQMath/data-indexed/task2_2022_latex_L8.mindex

data/ARQMath/data-indexed/task2_2022_latex_L8.mindex.meta: data/ARQMath/data-indexed/task2_2022_latex_L8.mindex src_2022/mtextsearch/mencode.exe
	src_2022/mtextsearch/mencode.exe data/ARQMath/data-indexed/task2_2022_latex_L8.mindex

index-task1: data/ARQMath/data-indexed/task1_2022_L8.mindex.meta

index-task2: data/ARQMath/data-indexed/task2_2022_latex_L8.mindex.meta

# ------------------ QUERY ------------------
data/ARQMath/data-queried/topics-task1-2020.xml data/ARQMath/data-queried/topics-task1-2021.xml data/ARQMath/data-queried/topics-task1-2022.xml \
data/ARQMath/data-queried/topics-task2-2020.xml data/ARQMath/data-queried/topics-task2-2021.xml data/ARQMath/data-queried/topics-task2-2022.xml: src_2022/query*.py
	python3 src_2022/query_prepro.py; python3 src_2022/query_postpro.py --output_folder data/ARQMath/data-queried/

data/ARQMath/data-queried/task1-%-L8_a018.tsv: data/ARQMath/data-queried/topics-task1-%.xml data/ARQMath/data-indexed/task1_2022_L8.mindex.meta \
  src_2022/mtextsearch src_2022/mtextsearch/mstrip.exe src_2022/mtextsearch/msearch.exe
	cat data/ARQMath/data-queried/topics-task1-$(*).xml \
	  | python3 src_2022/mathtuples/mathtuples/convert.py --context \
	  | ./src_2022/mtextsearch/mstrip.exe -q \
	  | ./src_2022/mtextsearch/msearch.exe -k1000 -M -a0.18 data/ARQMath/data-indexed/task1_2022_L8.mindex \
	  | awk 'BEGIN{OFS="\t"} {split($$2,a,"_"); $$2=a[3]; print $$0"\tL8_a018"}' \
	  > data/ARQMath/data-queried/task1-$(*)-L8_a018.tsv

data/ARQMath/data-queried/trec-task1-%.tsv: data/ARQMath/data-queried/task1-%.tsv
	awk 'BEGIN{OFS="\t"} {$$2="Q0\t"$$2; print}' data/ARQMath/data-queried/task1-$(*).tsv > data/ARQMath/data-queried/trec-task1-$(*).tsv

data/ARQMath/data-queried/task2-%-latex_L8_a040.tsv: data/ARQMath/data-queried/topics-task2-%.xml data/ARQMath/data-indexed/task2_2022_latex_L8.mindex.meta \
  src_2022/mtextsearch src_2022/mtextsearch/mstrip.exe src_2022/mtextsearch/msearch.exe
	cat data/ARQMath/data-queried/topics-task2-$(*).xml \
	  | python3 src_2022/latex_filter_stopwords.py -tsv inline \
	  | python3 src_2022/mathtuples/mathtuples/convert.py --context \
	  | ./src_2022/mtextsearch/mstrip.exe -q \
	  | ./src_2022/mtextsearch/msearch.exe -k1000 -M -a0.40 data/ARQMath/data-indexed/task2_2022_latex_L8.mindex \
	  | awk 'BEGIN{OFS="\t"} {split($$2,a,"_"); $$2=a[1]"\t"a[2]; print $$0"\tlatex_L8_a040"}' \
	  > data/ARQMath/data-queried/task2-$(*)-latex_L8_a040.tsv

data/ARQMath/data-queried/trec-task2-2020-%.tsv: data/ARQMath/data-queried/task2-2020-%.tsv
	python3 src_2022/dedup_task2.py -qre data/ARQMath/experiments/qrels_official_2020/qrel_task2 -tsv data/ARQMath/data-original/Formulas/latex_representation_v3/ data/ARQMath/data-queried/task2-2020-*.tsv

data/ARQMath/data-queried/trec-task2-2021-%.tsv: data/ARQMath/data-queried/task2-2021-%.tsv
	python3 src_2022/dedup_task2.py -qre data/ARQMath/experiments/qrels_official_2021/qrel_task2 -tsv data/ARQMath/data-original/Formulas/latex_representation_v3/ data/ARQMath/data-queried/task2-2021-*.tsv

data/ARQMath/data-queried/trec-task2-2022-%.tsv: data/ARQMath/data-queried/task2-2022-%.tsv
	python3 src_2022/dedup_task2.py -qre data/ARQMath/experiments/qrels_official_2022/qrel_task2 -tsv data/ARQMath/data-original/Formulas/latex_representation_v3/ data/ARQMath/data-queried/task2-2022-*.tsv

query-task1: data/ARQMath/data-queried/trec-task1-2020-L8_a018.tsv data/ARQMath/data-queried/trec-task1-2021-L8_a018.tsv data/ARQMath/data-queried/trec-task1-2022-L8_a018.tsv

query-task2: data/ARQMath/data-queried/trec-task2-2020-latex_L8_a040.tsv data/ARQMath/data-queried/trec-task2-2021-latex_L8_a040.tsv data/ARQMath/data-queried/trec-task2-2022-latex_L8_a040.tsv

# ------------------ EVAL ------------------
trec_eval:
	git clone https://github.com/usnistgov/trec_eval.git; cd trec_eval; make

eval-task1-%: query-task1 trec_eval
	./trec_eval/trec_eval -l2 -m num_q -m ndcg -m P.10 -m map -J data/ARQMath/experiments/qrels_official_2020/qrel_task1 data/ARQMath/data-queried/trec-task1-2020-$(*).tsv; \
	./trec_eval/trec_eval -l2 -m num_q -m ndcg -m P.10 -m map -J data/ARQMath/experiments/qrels_official_2021/qrel_task1 data/ARQMath/data-queried/trec-task1-2021-$(*).tsv; \
	./trec_eval/trec_eval -l2 -m num_q -m ndcg -m P.10 -m map -J data/ARQMath/experiments/qrels_official_2022/qrel_task1 data/ARQMath/data-queried/trec-task1-2022-$(*).tsv

eval-task2-%: query-task2 trec_eval
	./trec_eval/trec_eval -l2 -m num_q -m ndcg -m P.10 -m map -J data/ARQMath/experiments/qrels_official_2020/qrel_task2 data/ARQMath/data-queried/trec-task2-2020-$(*).tsv; \
	./trec_eval/trec_eval -l2 -m num_q -m ndcg -m P.10 -m map -J data/ARQMath/experiments/qrels_official_2021/qrel_task2 data/ARQMath/data-queried/trec-task2-2021-$(*).tsv; \
	./trec_eval/trec_eval -l2 -m num_q -m ndcg -m P.10 -m map -J data/ARQMath/experiments/qrels_official_2022/qrel_task2 data/ARQMath/data-queried/trec-task2-2022-$(*).tsv

eval: eval-task1-L8_a018 eval-task2-latex_L8_a040

