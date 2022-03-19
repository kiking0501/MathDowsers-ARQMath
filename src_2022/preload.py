from config import ARQM_PREPRO_PATH, ARQM_FINAL_HTML_MINIMAL_PATH
import os


def get_html_manifest():
    """
        a txt file with each line
            folder_path_suffix min-thread-id max-thread-id
        (separated by \t)

        e.g.
        /1_2010/1_07    1   1329
        /1_2010/1333_08 1333    3750
    """
    html_manifest = {}
    with open(os.path.join(ARQM_PREPRO_PATH, "html-manifest.txt")) as f:
        for l in f.readlines():
            path, st, et = l.strip().split('\t')
            html_manifest[path] = (int(st), int(et))
    return html_manifest

HTML_MANIFEST = get_html_manifest()


def get_date2folder_map():
    """
        a dict {year -> month -> folder_path_suffix}

        e.g. {2010: {7 : "/1_2010/1_07",
                     8 : "/1_2010/1333_08"}}
    """
    date2folder_map = {}
    for k in sorted(HTML_MANIFEST.keys(), key=lambda x: int(x.split('/')[1].partition('_')[2])):
        _, year, month = k.split('/')
        year = int(year.partition('_')[2])
        month = int(month.partition('_')[2])
        if year not in date2folder_map:
            date2folder_map[year] = {}
        date2folder_map[year][month] = k
    return date2folder_map

DATE2FOLDER_MAP = get_date2folder_map()


def html_folder_lookup(thread_id, directory=ARQM_FINAL_HTML_MINIMAL_PATH):
    result = None
    for path, (st, et) in HTML_MANIFEST.items():
        if thread_id >= st and thread_id <= et:
            folder_path = os.path.join(directory+path, str(thread_id))
            if os.path.exists(folder_path):
                result = folder_path
    if result is None:
        print("%s not found!" % thread_id)
    return result
