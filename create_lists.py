import sys, os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "data_creation")))

from gatherPlayers import extractPickle, addToPickle

def main():

    inputs1 = extractPickle('twoD_list.pickle', 2014)[150:]
    inputs2 = extractPickle('twoD_list.pickle', 2015)[150:]
    inputs3 = extractPickle('twoD_list.pickle', 2017)[150:]
    inputs4 = extractPickle('twoD_list.pickle', 2018)[150:]
    inputs5 = extractPickle('twoD_list.pickle', 2019)[150:]
    inputs6 = extractPickle('twoD_list.pickle', 2020)[150:]

    outputs1 = extractPickle('outcome_vectors.pickle', 2014)[150:]
    outputs2 = extractPickle('outcome_vectors.pickle', 2015)[150:]
    outputs3 = extractPickle('outcome_vectors.pickle', 2017)[150:]
    outputs4 = extractPickle('outcome_vectors.pickle', 2018)[150:]
    outputs5 = extractPickle('outcome_vectors.pickle', 2019)[150:]
    outputs6 = extractPickle('outcome_vectors.pickle', 2020)[150:]

    inputs  = inputs1  + inputs2  + inputs3  + inputs4  + inputs5  + inputs6
    outputs = outputs1 + outputs2 + outputs3 + outputs4 + outputs5 + outputs6

    print("Inputs length: {}".format(len(inputs)))
    print("Outputs length: {}".format(len(outputs)))

    addToPickle(inputs, 'data_to_use.pickle', 1)
    addToPickle(outputs, 'outputs_to_use.pickle', 1)

if __name__ == '__main__':
    main()
