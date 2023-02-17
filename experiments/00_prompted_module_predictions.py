import pickle as pkl
from mprompt.modules.prompted_module import PromptedModule
from mprompt.llm import llm_hf
import random
import torch
import numpy as np
from mprompt.data.data import TASKS, TASKS_TOY, TASKS_D3
from os.path import join, dirname
from tqdm import tqdm
import os
path_to_repo = dirname(dirname(os.path.abspath(__file__)))


def calculate_mean_preds_matrix_over_tasks(mod, task_names, assert_checks=False):
    """Calculate mean predictions using prompts from different modules.
    Matrix is (n_tasks, n_tasks) where each entry is the mean prediction
    Each row uses a different prompt in the task and each column evaluates on examples from different tasks
    """
    n = len(task_names)
    mean_preds_matrix = np.zeros((n, n))

    for r, task_str in enumerate(tqdm(task_names)):
        # decide which task we are going to predict for
        print('\ntask_str', task_str)
        mod._init_task(task_str)
        X = TASKS[task_str]['examples']

        # print generations
        # generations = mod.generate(X)
        # for gen in generations:
            # print(gen)

        # calculate correct preds
        pred = mod(X)
        probs_pos = {
            x: p for x, p in zip(X, pred)
        }

        # calculate probs for other categories
        probs_baseline = {}
        for c, task_str_baseline in enumerate(task_names):
            if task_str_baseline == task_str:
                mean_preds_matrix[r, c] = np.mean(list(probs_pos.values()))
            else:
                X = TASKS[task_str_baseline]['examples']
                pred = mod(X)
                probs_baseline.update({
                    x: p for x, p in zip(X, pred)
                })
                mean_preds_matrix[r, c] = np.mean(list(probs_baseline.values()))

        print('\n\n')
        if assert_checks:
            for k in sorted(probs_pos, key=probs_pos.get, reverse=True):
                print(f'\t{k} {probs_pos[k]:.2e}')
            print('\t-------------------')
            for k in sorted(probs_baseline, key=probs_baseline.get, reverse=True):
                print(f'\t{k} {probs_baseline[k]:.2e}')

            vals = np.array(list(probs_pos.values()))
            vals_baseline = np.array(list(probs_baseline.values()))
            assert np.mean(vals) > np.mean(vals_baseline), \
                f'mean for inputs in {task_str} should be higher for positive examples'
            assert np.min(vals) > np.max(vals_baseline), \
                f'min for pos inputs should be greater than max for neg inputs in {task_str}'

    return mean_preds_matrix


def test_mean_preds_matrix():
    mod = PromptedModule(
        checkpoint='gpt2',
    )
    task_names = list(TASKS_TOY.keys())
    mean_preds_matrix = calculate_mean_preds_matrix_over_tasks(
        mod, task_names, assert_checks=True)

if __name__ == '__main__':
    np.random.seed(1)
    random.seed(1)
    torch.manual_seed(1)

    # checkpoint = 'gpt2-xl'
    # checkpoint = 'facebook/opt-iml-max-30b'
    # task_names = list(TASKS_D3.keys())
    # mod = PromptedModule(
    #     checkpoint=checkpoint,
    # )
    # mean_preds_matrix = calculate_mean_preds_matrix_over_tasks(
    #     mod, task_names, assert_checks=False)
    # pkl.dump(mean_preds_matrix,
    #          open(join(path_to_repo, 'results', f'mean_preds_matrix_d3___{checkpoint.replace("/", "__")}.pkl'), 'wb'))

    test_mean_preds_matrix()