import traceback

from Constants import Acties
from Controller import Controller
from View import View

def main():
    try:
        controller = Controller()
        app = View.get()

        app.set_controller(controller)

        app.run()
    except Exception as e:
        app.set_exception(e, traceback.print_exc())

if __name__ == "__main__":
    main()



