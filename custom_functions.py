from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import precision_score, recall_score, accuracy_score, f1_score
from yellowbrick.classifier import ConfusionMatrix


def pitch_counter(df):
    '''Creates and populates a `Pitch_Per_Game` column in DataFrame, giving
    each row an updated pitch-count for each pitch thrown per game.

    Args:
        df (DataFrame): DataFrame on which to create and populate
        `Pitch_Per_Game` column.

    Returns:
        DataFrame.head(): Preview of first five rows of updated DataFrame.
    '''
    # create pitch-per-game column
    df['Pitch_Per_Game'] = 0
    # start counter at 1
    i = 1
    for index in range(len(df)):
        try:
            # when next pitch is thrown on same date as the current pitch
            if df['Game_Date'][index] == df['Game_Date'][index + 1]:
                # increase pitch_per_game of current pitch by i
                df['Pitch_Per_Game'][index] += i
                # add 1 to i
                i += 1
            # when next pitch is thrown on different date as the current pitch
            else:
                # increase pitch_per_game of current pitch by i
                df['Pitch_Per_Game'][index] += i
                # reset i
                i = 1
        # necessary for last row, when there is no "next pitch"
        except KeyError:
            # increase pitch_per_game of current pitch by i
            df['Pitch_Per_Game'][index] += i
    return df.head()


def rest_days(df):
    '''Creates and populates a `Days_Between_Starts` column in DataFrame,
    giving each row a value for the number of days off between the current
    game and the previous game. The first game of each season defaults to '4',
    which is considered normal rest for a starting pitcher.

    Args:
        df (DataFrame): DataFrame on which to create and populate
        `Days_Between_Starts` column.

    Returns:
        int64: Value-counts of each unique value in `Days_Between_Starts`
        column.
    '''
    df['Days_Between_Starts'] = np.nan
    for index in range(len(df)):
        # first pitch of dataframe
        if index == 0:
            # use '4' as placeholder for normal rest
            df['Days_Between_Starts'][index] = 4
        # first pitch of new season
        elif df.Game_Date[index].year != df.Game_Date[index - 1].year:
            # use '4' as placeholder for normal rest
            df['Days_Between_Starts'][index] = 4
        # first pitch of game
        elif df['Pitch_Per_Game'][index] == 1:
            # number of days between current date and previous date
            rest = df.Game_Date[index].date() - df.Game_Date[index - 1].date()
            rest = rest.days - 1
            df['Days_Between_Starts'][index] = rest
        else:
            continue
    df['Days_Between_Starts'].fillna(method='ffill', inplace=True)
    return df['Days_Between_Starts'].value_counts()


def find_best_k(X_train, y_train, X_test, y_test, min_k=1, max_k=25):
    '''Trains K-Nearest Neighbors classifier on passed training and
    testing subsets, for every odd k value between min_k and max_k.
    Returns evaluation metrics resulting from classifier with
    optimal k value, and a confusion matrix.

    Args:
        X_train (ndarray): Train subset X (data)
        y_train (Series): Train subset y (predictions)
        X_test (ndarray): Test subset X (data)
        y_test (Series): Test subset y (predictions)
        min_k (int): Minimum value for best K
        max_k (int): Maximum value for best K

    Returns:
        string: "Best Value for k: {}"
        string: "Accuracy: {}"
        string: "Precision: {}"
        string: "Recall: {}"
        string: "F1-Score: {}"
        plot: Confusion Matrix

    '''
    best_k = 0
    best_score = 0.0
    for k in range(min_k, max_k+1, 2):
        # Instantiate KNeighborsClassifier
        knn = KNeighborsClassifier(n_neighbors=k)
        # Fit the classifier
        knn.fit(X_train, y_train)
        # Predict on the test set
        preds = knn.predict(X_test)
        accuracy = accuracy_score(y_test, preds)
        precision = precision_score(y_test, preds, average='macro')
        recall = recall_score(y_test, preds, average='macro')
        f1 = f1_score(y_test, preds, average='macro')
        if f1 > best_score:
            best_k = k
            best_score = f1
    cm = ConfusionMatrix(knn, classes=y_train.unique())
    cm.score(X_test, y_test)
    print("Best Value for k: {}".format(best_k))
    print("Accuracy: {}".format(round(accuracy,3)))
    print("Precision: {}".format(round(precision, 3)))
    print("Recall: {}".format(round(recall, 3)))
    print("F1-Score: {}".format(round(best_score, 3)))
    plt.tight_layout()
    cm.show()
    

def boxplot(data):
    metrics = ['Release_Speed', 'Release_Point_X', 'Release_Point_Y',
               'Release_Point_Z', 'Horizontal_Movement', 'Vertical_Movement',
               'Velocity_X', 'Velocity_Y', 'Velocity_Z', 'Acceleration_X',
               'Acceleration_Y', 'Acceleration_Z', 'Perceived_Speed',
               'Release_Spin_Rate', 'Release_Extension']
    sns.set(style="darkgrid", context='notebook')
    for metric in metrics:
        plt.figure(figsize=(8,5))
        sns.boxplot(x='Pitch_Name', y=metric, data=data)
        plt.title('Distribution of "{}" by Pitch Type'.format(metric.replace('_', ' ')))
        plt.xlabel('Pitch Type')
        plt.ylabel(metric.replace('_', ' '))
        plt.tight_layout()
        

def Cohen_d(group1, group2):
    '''Compute Cohen's d.
       
       group1: Series or NumPy array
       group2: Series or NumPy array

       returns a floating point number'''

    diff = group1.mean() - group2.mean()

    n1, n2 = len(group1), len(group2)
    var1 = group1.var()
    var2 = group2.var()

    # Calculate the pooled threshold
    pooled_var = (n1 * var1 + n2 * var2) / (n1 + n2)
    
    # Calculate Cohen's d statistic
    d = diff / np.sqrt(pooled_var)
    
    return abs(d)