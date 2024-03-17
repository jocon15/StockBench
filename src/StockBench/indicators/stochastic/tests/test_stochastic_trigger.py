import os
import sys

# allows import out a directory
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))


from StockBench.indicators.stochastic.trigger import StochasticTrigger


# create test object
test_object = StochasticTrigger('stochastic')


def test_additional_days():
    assert test_object.additional_days('stochastic', '>20') == 14

    assert test_object.additional_days('stochastic20', '>20') == 20

    assert test_object.additional_days('stochastic50$price', '>20') == 50

    assert test_object.additional_days('stochastic50$price', '>20') == 50

    assert test_object.additional_days('stochastic20$slope10', '>20') == 20

    assert test_object.additional_days('stochastic20$slope30', '>20') == 30
