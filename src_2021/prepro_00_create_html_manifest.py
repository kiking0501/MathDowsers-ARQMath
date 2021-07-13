"""
    Create a manifest file for easier traversal for the Thread HTML files
        according to the thread creation date

    Prerequisite:
        Thread HTML files by year has been downloaded at <ARQM_THREADS_YEAR_PATH>

    Effect:
        a manifest file for the HTML files will be created

    Run by "python <name of this python file>.py"
"""

from config import ARQM_THREADS_YEAR_PATH, ARQM_PREPRO_PATH
import os


def create_html_manifest(output_file, verbose=True):
    '''
        create a manifest-dict that stores:
            html-folder-path -> (start-html-id, end-html-id)
        for easier lookup

        e.g.
              /1_2010/106814_03 |-> (106814, 106814)
           /16020_2011/16020_01 |-> (16020, 19782)
    '''

    ### get sorted path list
    path_list = []
    for root, _, _ in os.walk(ARQM_THREADS_YEAR_PATH):
        p = root.replace(ARQM_THREADS_YEAR_PATH, "")
        if p and len(p.split('/')) == 3:
            path_list.append(p)

    sort_list = sorted(
        path_list, key=lambda x:
            (int(x.partition('/')[2].partition('/')[0].partition('_')[0]),
             int(x.rpartition('/')[2].partition('_')[0])))

    ### get range of html ids
    range_dict = {}
    for ind, p in enumerate(sort_list):
        #print(p)
        st = int(p.split('/')[2].partition('_')[0])
        for _, _, htmls in os.walk(ARQM_THREADS_YEAR_PATH+p):
            et = int(sorted(htmls, key=lambda x: int(x.partition('.')[0]))[-1].partition('.')[0])
        range_dict[p] = (st, et)

    if verbose:
        for ind, p in enumerate(sort_list):
            print("%20s" % p, "|->", range_dict[p])

    with open(output_file, "w") as f:
        for ind, p in enumerate(sort_list):
            f.write('%s\t%s\t%s\n' % (p, range_dict[p][0], range_dict[p][1]))
        print("%s saved." % f.name)

    return range_dict


if __name__ == '__main__':
    create_html_manifest(
        os.path.join(ARQM_PREPRO_PATH, "html-manifest.txt")
    )
