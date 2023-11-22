import matplotlib
import numpy as np
import matplotlib.pyplot as plt
from typing import List
import seaborn as sns
import numpy as np
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt
import adjustText
# import matplotlib.colormaps

# default matplotlib colors
cs_mpl = [
    "#1f77b4",
    "#ff7f0e",
    "#2ca02c",
    "#d62728",
    "#9467bd",
    "#8c564b",
    "#e377c2",
    "#7f7f7f",
    "#bcbd22",
    "#17becf",
]

# a nice blue/red color
cblue = "#66ccff"
cred = "#cc0000"


def imshow_diverging(mat):
    vabs = np.nanmax(np.abs(mat))
    plt.imshow(mat, cmap=sns.diverging_palette(
        29, 220, as_cmap=True), vmin=-vabs, vmax=vabs)
    plt.colorbar(label='Mean response ($\sigma_f$)')


def save_figs_to_single_pdf(filename):
    p = PdfPages(filename)
    fig_nums = plt.get_fignums()
    figs = [plt.figure(n) for n in fig_nums]
    for fig in figs:
        fig.savefig(p, format="pdf", bbox_inches="tight")
    p.close()


def colorize(
    words: List[str],
    color_array,  # : np.ndarray[float],
    char_width_max=60,
    title: str = None,
    subtitle: str = None,
):
    """
    Colorize a list of words based on a color array.
    color_array
        an array of numbers between 0 and 1 of length equal to words
    """
    cmap = matplotlib.colormaps.get_cmap("viridis")
    # cmap = matplotlib.cm.get_cmap('viridis_r')
    template = (
        '<span class="barcode"; style="color: black; background-color: {}">{}</span>'
    )
    # template = '<span class="barcode"; style="color: {}; background-color: white">{}</span>'
    colored_string = ""
    char_width = 0
    for word, color in zip(words, color_array):
        char_width += len(word)
        color = matplotlib.colors.rgb2hex(cmap(color)[:3])
        colored_string += template.format(color, "&nbsp" + word + "&nbsp")
        if char_width >= char_width_max:
            colored_string += "</br>"
            char_width = 0

    if subtitle:
        colored_string = f"<h5>{subtitle}</h5>\n" + colored_string
    if title:
        colored_string = f"<h3>{title}</h3>\n" + colored_string
    return colored_string


def moving_average(a, n=3):
    assert n % 2 == 1, "n should be odd"
    diff = n // 2
    vals = []
    # calculate moving average in a window 2
    # (1, 4)
    for i in range(diff, len(a) + diff):
        l = i - diff
        r = i + diff + 1
        vals.append(np.mean(a[l:r]))
    return np.nan_to_num(vals)


def get_story_scores(val, expls, paragraphs):
    import imodelsx.util

    # mod = EmbDiffModule()
    scores_list = []
    for i in range(len(expls)):
        # for i in range(1):
        expl = expls[i].lower()
        text = paragraphs[i]
        words = text.split()

        ngrams = imodelsx.util.generate_ngrams_list(text.lower(), ngrams=3)
        ngrams = [words[0], words[0] + " " + words[1]] + ngrams

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
        # s = sasc.viz.colorize(words, neg_dists, title=expl, subtitle=prompt)

        # validator-based viz
        probs = np.array(val.validate_w_scores(expl, ngrams))
        scores_list.append(probs)
    return scores_list


def heatmap(
    data,
    labels,
    xlab="Explanation for matching",
    ylab="Explanation for generation",
    clab="Fraction of matching ngrams",
    diverging=True,
):
    # plt.style.use('dark_background')
    plt.figure(figsize=(7, 6))
    if diverging:
        imshow_diverging(data)
    else:
        plt.imshow(data)
        plt.colorbar(label=clab)
    plt.xticks(range(data.shape[0]), labels, rotation=90, fontsize="small")
    plt.yticks(range(data.shape[1]), labels, fontsize="small")
    plt.ylabel(ylab)
    plt.xlabel(xlab)
    plt.tight_layout()
    # plt.show()


def quickshow(X: np.ndarray, subject="UTS03", fname_save=None, title=None):
    import cortex

    """
    Actual visualizations
    Note: for this to work, need to point the cortex config filestore to the `ds003020/derivative/pycortex-db` directory.
    This might look something like `/home/chansingh/mntv1/deep-fMRI/data/ds003020/derivative/pycortex-db/UTS03/anatomicals/`
    """
    vol = cortex.Volume(X, subject, xfmname=f"{subject}_auto")
    # , with_curvature=True, with_sulci=True)
    vabs = max(abs(vol.data.min()), abs(vol.data.max()))
    vol.vmin = -vabs
    vol.vmax = vabs
    # fig = plt.figure()
    # , vmin=-vabs, vmax=vabs)
    cortex.quickshow(vol, with_rois=True, cmap="PuBu")
    # fig = plt.gcf()
    # add title
    # fig.axes[0].set_title(title, fontsize='xx-small')
    if fname_save is not None:
        plt.savefig(fname_save)
        plt.savefig(fname_save.replace(".pdf", ".png"))
        plt.close()


def outline_diagonal(shape, color='gray', lw=1, block_size=1):
    for r in range(shape[0]):
        for c in range(shape[1]):
            # outline the diagonal with blocksize 1
            if block_size == 1 and r == c:
                plt.plot([r - 0.5, r + 0.5],
                         [c - 0.5, c - 0.5], color=color, lw=lw)
                plt.plot([r - 0.5, r + 0.5],
                         [c + 0.5, c + 0.5], color=color, lw=lw)
                plt.plot([r - 0.5, r - 0.5],
                         [c - 0.5, c + 0.5], color=color, lw=lw)
                plt.plot([r + 0.5, r + 0.5],
                         [c - 0.5, c + 0.5], color=color, lw=lw)
            if block_size == 2 and r == c and r % 2 == 0:
                rx = r + 0.5
                cx = c + 0.5
                plt.plot([rx - 1, rx + 1], [cx - 1, cx - 1],
                         color=color, lw=lw)
                plt.plot([rx - 1, rx + 1], [cx + 1, cx + 1],
                         color=color, lw=lw)
                plt.plot([rx - 1, rx - 1], [cx - 1, cx + 1],
                         color=color, lw=lw)
                plt.plot([rx + 1, rx + 1], [cx - 1, cx + 1],
                         color=color, lw=lw)
            if block_size == 3 and r == c and r % 3 == 0:
                rx = r + 1
                cx = c + 1
                plt.plot([rx - 1.5, rx + 1.5],
                         [cx - 1.5, cx - 1.5], color=color, lw=lw)
                plt.plot([rx - 1.5, rx + 1.5],
                         [cx + 1.5, cx + 1.5], color=color, lw=lw)
                plt.plot([rx - 1.5, rx - 1.5],
                         [cx - 1.5, cx + 1.5], color=color, lw=lw)
                plt.plot([rx + 1.5, rx + 1.5],
                         [cx - 1.5, cx + 1.5], color=color, lw=lw)


def plot_annotated_resp(
    voxel_num: int,
    word_chunks,
    voxel_resp,
    expl_voxel,
    start_times,
    end_times,
    stories_data_dict,
    expls,
    story_num,
    word_chunks_contain_example_ngrams,
    trim=5,
):
    plt.figure(figsize=(22, 6))
    plt.plot(voxel_resp)

    # annotate top 5 voxel_resps with word_chunks
    texts = []
    top_5_resp_positions = np.argsort(voxel_resp)[::-1][:5]
    for i, resp_position in enumerate(top_5_resp_positions):
        plt.plot(resp_position, voxel_resp[resp_position], "o", color="black")
        text = (
            " ".join(word_chunks[resp_position - 1])
            + "\n"
            + " ".join(word_chunks[resp_position])
        )
        texts.append(
            plt.annotate(
                text, (resp_position,
                       voxel_resp[resp_position]), fontsize="x-small"
            )
        )

    # annotate bottom 5 voxel_resps with word_chunks
    bottom_5_resp_positions = np.argsort(voxel_resp)[:5]
    for i, resp_position in enumerate(bottom_5_resp_positions):
        plt.plot(resp_position, voxel_resp[resp_position], "o", color="black")
        text = (
            " ".join(word_chunks[resp_position - 2])
            + "\n"
            + " ".join(word_chunks[resp_position - 1])
            + "\n"
            + " ".join(word_chunks[resp_position])
        )
        texts.append(
            plt.annotate(
                text, (resp_position,
                       voxel_resp[resp_position]), fontsize="x-small"
            )
        )

    # plot key ngrams
    i_start_voxel = start_times[voxel_num]
    i_end_voxel = end_times[voxel_num] + 1
    if i_end_voxel > len(voxel_resp):
        i_end_voxel = len(voxel_resp)
    idxs = np.arange(i_start_voxel, i_end_voxel)
    idxs_wc = np.where(word_chunks_contain_example_ngrams[idxs])[0]
    plt.plot(idxs, voxel_resp[idxs], color="C0", linewidth=2)
    plt.plot(idxs[idxs_wc], voxel_resp[idxs[idxs_wc]],
             "^", color="C1", linewidth=2)

    # clean up plot and add in trim
    adjustText.adjust_text(texts, arrowprops=dict(
        arrowstyle="->", color="gray"))
    plt.grid(alpha=0.4, axis="y")
    xticks = np.array([start_times - trim, end_times - trim]).mean(axis=0)
    plt.xticks(xticks, expls, rotation=45, fontsize="x-small")

    for i, (start_time, end_time) in enumerate(zip(start_times - trim, end_times - trim)):
        if i == voxel_num:
            plt.axvspan(start_time, end_time, facecolor="green", alpha=0.1)
        elif i % 2 == 0:
            plt.axvspan(start_time, end_time, facecolor="gray", alpha=0.1)
        else:
            plt.axvspan(start_time, end_time, facecolor="gray", alpha=0.0)

    plt.ylabel(
        f'"{expl_voxel}" voxel response\n({stories_data_dict["story_name_new"][story_num][3:-10]})'
    )

    # plt.show()
