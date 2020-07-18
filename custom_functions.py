from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import precision_score, recall_score, accuracy_score, f1_score


def pitch_counter(df):
    '''Creates and populates a `pitch_per_game` column in DataFrame, giving
    each row an updated pitch-count for each pitch thrown per game.

    Args:
        df (DataFrame): DataFrame on which to create and populate
        `pitch_per_game` column.

    Returns:
        DataFrame.head(): Preview of first five rows of updated DataFrame.
    '''
    # create pitch-per-game column
    df['pitch_per_game'] = 0
    # start counter at 1
    i = 1
    for index in range(len(df)):
        try:
            # when next pitch is thrown on same date as the current pitch
            if df['game_date'][index] == df['game_date'][index + 1]:
                # increase pitch_per_game of current pitch by i
                df['pitch_per_game'][index] += i
                # add 1 to i
                i += 1
            # when next pitch is thrown on different date as the current pitch
            else:
                # increase pitch_per_game of current pitch by i
                df['pitch_per_game'][index] += i
                # reset i
                i = 1
        # necessary for last row, when there is no "next pitch"
        except KeyError:
            # increase pitch_per_game of current pitch by i
            df['pitch_per_game'][index] += i
    return df.head()


def find_best_k(X_train, y_train, X_test, y_test, min_k=1, max_k=25):
    '''Trains K-Nearest Neighbors classifier on passed training and
    testing subsets, for every odd k value between min_k and max_k.
    Returns evaluation metrics resulting from classifier with
    optimal k value.

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
    return ("Best Value for k: {}".format(best_k),
        "Accuracy: {}".format(accuracy),
        "Precision: {}".format(precision),
        "Recall: {}".format(recall),
        "F1-Score: {}".format(best_score))