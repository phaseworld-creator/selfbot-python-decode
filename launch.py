import sys, os, subprocess

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gui.dashboard import main



def install_requirements():

    try:


        subprocess.check_call(

            [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"]

        )

        print("All requirements installed successfully!")

    except subprocess.CalledProcessError as e:

        print(f"An error occurred while installing requirements: {e}")

        sys.exit(1)

    except FileNotFoundError:

        print("Error: 'requirements.txt' file not found.")

        sys.exit(1)





if __name__ == "__main__":


    install_requirements()



if __name__ == "__main__":

    main() 
