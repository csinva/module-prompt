import matplotlib
import numpy as np
import matplotlib.pyplot as plt
from typing import List
import imodelsx.util

from mprompt.methods.m4_evaluate import D5_Validator

def colorize(words: List[str], color_array: np.ndarray[float],
             char_width_max=60, title: str=None, subtitle: str=None):
    '''
    Colorize a list of words based on a color array.
    color_array
        an array of numbers between 0 and 1 of length equal to words
    '''
    cmap = matplotlib.cm.get_cmap('viridis')
    template = '<span class="barcode"; style="color: black; background-color: {}">{}</span>'
    colored_string = ''
    char_width = 0
    for word, color in zip(words, color_array):
        char_width += len(word)
        color = matplotlib.colors.rgb2hex(cmap(color)[:3])
        colored_string += template.format(color, '&nbsp' + word + '&nbsp')
        if char_width >= char_width_max:
            colored_string += '</br>'
            char_width = 0

    if subtitle:
        colored_string = f'<h5>{subtitle}</h5>\n' + colored_string
    if title:
        colored_string = f'<h3>{title}</h3>\n' + colored_string
    return colored_string

def moving_average(a, n=3):
    assert n % 2 == 1, 'n should be odd'
    diff = n // 2
    vals = []
    # calculate moving average in a window 2
    # (1, 4)
    for i in range(diff, len(a) + diff):
        l = i - diff
        r = i + diff + 1
        vals.append(np.mean(a[l: r]))
    return np.nan_to_num(vals)


def visualize_story_html(val, expls, paragraphs, prompts, fname='../results/story_running.html'):
    # mod = EmbDiffModule()
    
    story_running = ''
    for i in range(len(expls)):
    # for i in range(1):
        expl = expls[i].lower()
        text = paragraphs[i]
        words = text.split()
        prompt = prompts[i]

        ngrams = imodelsx.util.generate_ngrams_list(text.lower(), ngrams=3)
        ngrams = [words[0], words[0] + ' ' + words[1]] + ngrams

        # # embdiff-based viz
        # mod._init_task(expl)    
        # neg_dists = mod(ngrams)
        # assert len(ngrams) == len(words) == len(neg_dists)
        # # neg_dists = scipy.special.softmax(neg_dists)
        # # plt.plot(neg_dists)
        # # plt.plot(moving_average(neg_dists, n=5))
        # neg_dists = moving_average(neg_dists, n=3)
        # neg_dists = (neg_dists - neg_dists.min()) / (neg_dists.max() - neg_dists.min())
        # neg_dists = neg_dists / 2 + 0.5 # shift to 0.5-1 range
        # s = mprompt.viz.colorize(words, neg_dists, title=expl, subtitle=prompt)

        # validator-based viz
        probs = np.array(val.validate_w_scores(expl, ngrams))
        probs_disp = moving_average(probs, n=3)
        probs_disp = probs_disp / 2 + 0.5 # shift to 0.5-1 range
        s = colorize(words, probs_disp, title=expl, subtitle=prompt)
        
        # viz
        # display(HTML(s))
        story_running += ' ' + s

    with open(fname, 'w') as f:
        f.write(story_running)
    return s

def heatmap(data, labels, xlab='Explanation for matching', ylab='Explanation for generation', clab='Fraction of matching ngrams'):
    plt.style.use('dark_background')
    plt.figure(figsize=(6, 5))
    plt.imshow(data)
    plt.xticks(range(data.shape[0]), labels, rotation=90)
    plt.yticks(range(data.shape[0]), labels)
    plt.ylabel(ylab)
    plt.xlabel(xlab)
    plt.colorbar(label=clab)
    plt.tight_layout()
    plt.show()