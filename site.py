#!/usr/bin/env python
# -*- coding: utf-8 -*-
from bottle import *
from utils import *
from globals import *
import itertools

#
# reload(sys)
# sys.setdefaultencoding('utf-8')


global active_algos
global num_results


@get('')
@get('/')  # @route('/login')
@get('/cyber')
@get('/w2v')
@get('/heb-w2v')
def get_menu():
    return menu_text


@post('/choose_algo')
@get('/choose_algo')
def choose_algo():
    html = ' <b size="6"> Select wanted algorithms <br>'
    html += '<form action="algo_selected" method="post">'
    for algo in sorted(words_dict.keys()):
        html += '<input type="checkbox" name="{0}" value=1> {0}<br>'.format(algo)
    html += '<input type="submit" value="Submit"></form>'
    return html


@post('/update_num_results')
@get('/update_num_results')
def update_wanted_algos():
    global active_algos
    active_algos = []
    for algo in words_dict.keys():
        if request.forms.get(algo):
            active_algos.append(algo)
    active_algos = sorted(active_algos)
    return menu_text


@post('/algo_selected')
@get('/algo_selected')
def update_num_results():
    global num_results
    wanted_num_results = request.forms.get('num_results')
    num_results = wanted_num_results
    return menu_text


@post('/similar')
@get('/similar')
def search():
    f = open(search_result_file, 'a')
    wanted = request.forms.get('wanted')
    if not wanted:
        return "<p size='4'>Please enter a word</p>"
    text = menu_text
    text += "<p align='center'><b  size='5'>Current searching for words similar to-&nbsp&nbsp&nbsp" + wanted + "</b><br>"
    for algo in active_algos:
        cur_algo_words = words_dict[algo]
        cur_algo_vectors = vectors_dict[algo]
        f.write("Algo: " + algo + "\n")
        text += "<b align = 'center'><br> Algorithm: " + algo + "</b><br>"

        wanted_ind = search_for_word_as_part_of_pos(wanted, algo)
        try:
            wanted_ind = [cur_algo_words.index(as_appears_in_algo(wanted))]
        except:
            if len(wanted_ind) == 0:
                text += wanted + " is unknown, sorry."
                continue
        for word_ind in wanted_ind:
            f.write("\n\nCurrent searching for words similar to:" + cur_algo_words[word_ind] + "\n")
            text += "<br>Showing results for " + as_appear_in_site(cur_algo_words[word_ind]) + '<br><br>'
            print("here0")
            text += get_similar_to_site_and_file(cur_algo_vectors[word_ind], algo, f)
    return text + "</p>"


@post('/analogy')
@get('/analogy')
def analogy():
    f = open(analogy_result_file, 'a')
    input_words = [request.forms.get('word1'), request.forms.get('word2'), request.forms.get('word3')]
    for in_word in input_words:
        if not in_word:
            return "<p size='4'>Please enter all the words.</p>"
    text = menu_text
    for algo in active_algos:
        cur_algo_words = words_dict[algo]
        cur_algo_vectors = vectors_dict[algo]
        flag = False
        text += "<br> <b align='center' size='4'>Algorithm: " + algo + "</b><br><br>"
        f.write("Algo: " + algo + "\n")
        words_idx = []
        for in_word in input_words:
            cur_word_idx = search_for_word_as_part_of_pos(in_word, algo)
            try:
                cur_word_idx = [cur_algo_words.index(as_appears_in_algo(in_word))]
            except:
                if len(cur_word_idx) == 0:
                    text += in_word + " is unknown, sorry."
                    flag = True
            words_idx.append(cur_word_idx)

        if not flag:
            for input_pos_idx_option in list(itertools.product(*words_idx)):
                text += "<p align='center'><b  size='6'>Current looking for:<br>" + cur_algo_words[
                    input_pos_idx_option[2]] + " : word" + "<br>=<br>" + cur_algo_words[
                            input_pos_idx_option[1]] + " : " + cur_algo_words[input_pos_idx_option[0]] + "</b><br>"
                f.write("\n\nCurrent looking for:" + cur_algo_words[input_pos_idx_option[2]] + " : word = " +
                        cur_algo_words[input_pos_idx_option[1]] + " : " + cur_algo_words[
                            input_pos_idx_option[0]] + "\n")
                wanted = cur_algo_vectors[input_pos_idx_option[2]] - cur_algo_vectors[input_pos_idx_option[0]] + \
                         cur_algo_vectors[input_pos_idx_option[1]]
                text += get_similar_to_site_and_file(wanted, algo, f)
    return text + "</p>"


def get_similar_to_site_and_file(wanted, algo, f):
    print("here1")
    global num_results
    print("here2")
    text = ""
    print("here3")
    inds, sims = top_similar(wanted, vectors_dict[algo], results_to_show=num_results)
    print("pass call")
    print("found: ", len(inds))
    for i in range(len(inds)):
        text += "similarity:" + str(sims[i]) + "&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp" + \
                as_appear_in_site(words_dict[algo][inds[i]]) + "<br>"
        if i < MAX_RESULTS_PRINT_TO_FILE:
            f.write(words_dict[algo][inds[i]] + "\n")
    return text


def search_for_word_as_part_of_pos(wanted, algo):
    cur_algo_words = words_dict[algo]
    wanted_idx = []
    if multi_pos_dict[algo]:
        for i, word in enumerate(cur_algo_words):
            parts = word.split('_')
            if len(parts) > 1 and parts[1] == wanted:
                if len(parts) > 1 and parts[1] == wanted:
                    wanted_idx.append(i)
                    print cur_algo_words[i]
    return wanted_idx


def add_algorithm(path, name, multi_pos_flag=0):
    path = os.path.join('result', path)
    if not os.path.exists(os.path.join(path, "words_list.txt")):
        organize_data(path)
    with open(os.path.join(path, "words_list.txt"), 'r') as f:
        cur_words = f.readlines()
    cur_words = [word[:-1] for word in cur_words]
    cur_vecs = np.load(os.path.join(path, "words_vectors.npy"))
    words_dict[name] = cur_words
    vectors_dict[name] = cur_vecs
    multi_pos_dict[name] = multi_pos_flag


def main():
    global active_algos
    global num_results
    num_results = DEFAULT_NUM_RESULTS
    add_algorithm(path_FT, "fastText")
    add_algorithm(path_w2v, "w2v")
    # add_algorithm(path_FT_seg, "fastText seg")
    # add_algorithm(path_w2v_nn_win5, "w2v nn win 5")
    # add_algorithm(path_w2v_seg, "w2v seg")
    # add_algorithm(path_w2v_nn_win3, "w2v nn win 3")
    # add_algorithm(path_w2v_nn_win10, "w2v nn win 10")
    # add_algorithm(path_w2v_nn_win5_neg10, "w2v nn win 5 neg 10")
    add_algorithm(path_w2v_multi_pos, "w2v multi pos", 1)
    add_algorithm(path_FT_multi_pos, "fastText multi pos", 1)
    # add_algorithm(path_FT_nn, "fastText nn")
    add_algorithm(path_FT_nn_filtered, "fastText nn filtered")
    add_algorithm(path_w2v_nn_filtered, "w2v nn filtered")
    add_algorithm(path_odeds_algo_200, "Oded's algorithm 200 dim feature")
    add_algorithm(path_odeds_algo, "Oded's algorithm")
    add_algorithm(path_w2v_nn_pos_10, "w2v main (nn&pos) 10 feat", 1)
    add_algorithm(path_w2v_nn_pos_100, "w2v main (nn&pos) 100 feat", 1)
    add_algorithm(path_w2v_nn_pos_200, "w2v main (nn&pos) 200 feat", 1)
    add_algorithm(path_w2v_twitter, "w2v twitter", 0)
    add_algorithm(path_w2v_neg_20, "w2v nn&pos more negative(20)", 1)
    add_algorithm(path_w2v_neg_20_min_20, "w2v nn&pos more negative(20) and higher min", 1)
    active_algos = ["w2v main (nn&pos) 100 feat", "Oded's algorithm", "fastText multi pos", "w2v multi pos"]
    active_algos = sorted(active_algos)
    # run(host='77.126.119.142', port=80, debug=True)
    # run(host='192.168.1.15', port=80, debug=True)
    # run(host='localhost', port=7765, debug=False)
    run(host='', port=7765, debug=False)
    # run(host='132.71.121.195', port=8079, debug=False)


if __name__ == "__main__":
    words_dict = {}
    vectors_dict = {}
    multi_pos_dict = {}
    main()
    #

    # context = get_context_vec(join('result', path_w2v_nn_pos_10), ["לחם", "אב", "מלאכה", "ספר", "כנסת"],
    #                           words_dict['w2v main (nn&pos) 10 feat'])
    #
    # print get_similar_console(context, words_dict['w2v main (nn&pos) 10 feat'],
    #                           vectors_dict['w2v main (nn&pos) 10 feat'])
    #
    # context = get_context_vec(join('result', path_w2v_nn_pos_10), ["חוף", "סירה", "אוקיאנוס", "ים", "גלים"],
    #                           words_dict['w2v main (nn&pos) 10 feat'])
    #
    # print get_similar_console(context, words_dict['w2v main (nn&pos) 10 feat'],
    #                           vectors_dict['w2v main (nn&pos) 10 feat'])

    # active_algos = []
