from src.game import *
from os import path

if __name__ == '__main__':
    g = Game(path.dirname(__file__))
    
    while (1):    
        g.run()
        g.curr_menu.display_menu()