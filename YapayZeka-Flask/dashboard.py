import pandas as pd


def getvaluecounts(df):

    return dict(df['subject'].value_counts())


def getlevelcount(df):

    return dict(list(df.groupby(['level'])['num_subscribers'].count().items())[1:])


def getsubjectsperlevel(df):

    ans = list(dict(df.groupby(['subject'])['level'].value_counts()).keys())
    alllabels = [ans[i][0]+'_'+ans[i][1] for i in range(len(ans))]
    ansvalues = list(dict(df.groupby(['subject'])[
                    'level'].value_counts()).values())

    completedict = dict(zip(alllabels, ansvalues))

    return completedict


