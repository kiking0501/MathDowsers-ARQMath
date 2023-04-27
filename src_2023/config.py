import os

SRC_PATH = os.path.dirname(os.path.abspath(__file__))
BASE_PATH = os.path.dirname(SRC_PATH)
DATA_PATH = os.path.join(BASE_PATH, "data")

### raw data
ARQM_DATA_PATH = os.path.join(DATA_PATH, "ARQMath")
STORAGE_ARQM_DATA_PATH = os.path.join(ARQM_DATA_PATH, "data-original")

ARQM_FORMULAS_PATH = os.path.join(STORAGE_ARQM_DATA_PATH, "Formulas")
ARQM_TASK1_PATH = os.path.join(STORAGE_ARQM_DATA_PATH, "Task1")
ARQM_TASK2_PATH = os.path.join(STORAGE_ARQM_DATA_PATH, "Task2")


### generated data
ARQM_PREPRO_PATH = os.path.join(ARQM_DATA_PATH, "prepro_2022")


### Formula folders
FORMULA_FOLDER_CONFIG = {
    "latex": ("latex_representation_v3", range(1, 102)),
    "opt": ("opt_representation_v3", range(1, 102)),
    "slt": ("slt_representation_v3", range(1, 102)),
}

TASK_FORMULA_FOLDER_CONFIG = {
    2020: {
        "latex": os.path.join(ARQM_TASK1_PATH, "ARQMath_2020", "Topics", "Formula_topics_latex_V2.0.tsv"),
        "slt_original": os.path.join(ARQM_TASK1_PATH, "ARQMath_2020", "Topics", "Formula_topics_slt_V2.0.tsv"),
        "slt": os.path.join(ARQM_TASK1_PATH, "ARQMath_2021", "Topics", "Topics_2020_converted_Formula_slt_V2.0.tsv"),
    },
    2021: {
        "latex": os.path.join(ARQM_TASK1_PATH, "ARQMath_2021", "Formulas", "Topics_2021_Formulas_Latex_V1.1.tsv"),
        "slt": os.path.join(ARQM_TASK1_PATH, "ARQMath_2021", "Formulas", "Topics_2021_Formulas_SLT_V1.1.tsv"),
    },
    2022: {
        "latex": os.path.join(ARQM_TASK1_PATH, "ARQMath_2022", "Formulas", "Topics_Formulas_Latex.V0.1.tsv"),
        "slt": os.path.join(ARQM_TASK1_PATH, "ARQMath_2022", "Formulas", "Topics_Formulas_SLT.V0.1.tsv"),
    }
}
