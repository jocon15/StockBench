from isolation_testing.ema import run_ema
from isolation_testing.rsi import run_rsi
from isolation_testing.sma import run_sma
from isolation_testing.stochastic import run_stochastic

'''
This file is the solution to the issue where the plugin system could not access /plugins when
the application was run from the context of a single file in the /isolation_testing folder.

Mangling the pathname did not work. The workaround is to call the individual method defined 
in a singular method here to get the same application context as main_headless.py. 
'''


def main():
    # select a function to run:
    run_ema()
    run_sma()
    run_rsi()
    run_stochastic()


if __name__ == '__main__':
    main()
