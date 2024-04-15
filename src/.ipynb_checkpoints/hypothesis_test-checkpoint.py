from spicy import stats

def hypothesis_test(scores = [], mean_hypo = 0, sig_value = 0.05):
    t_statistic, p_value = stats.ttest_1samp(scores, mean_hypo)
    # print(p_value)
    if p_value < sig_value:
        return sum(scores)/len(scores)
    else: return -1