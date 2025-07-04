#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Optimalizace trasy pomocí metody Branch and Bound
Program pro optimalizaci cesty mezi body pomocí metody Branch and Bound
Autor: Matyáš Fric
"""

from gui.app import TSPOptimizerApp

def main():
    app = TSPOptimizerApp()
    app.mainloop()

if __name__ == "__main__":
    main()