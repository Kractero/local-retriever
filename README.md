# local-retriever

Run goldretriever locally. Gold retriever, for the uninformed, is a script that takes in NationStates puppets and outputs the bank, deck value, junk value, and optionally the packs and issues on each one.

## Usage
1. Clone/download this repository.
2. In config.py, set a user-agent (your main nation). If you want to get packs and issues also include the password.
3. Download dependencies, you can run either the bat file if on Windows, sh file if on Linux, or use the requirements.txt file to install the dependencies.
4. Run
   ```py
   python local_retriever.py
   ```
   If you want issues and packs, add the -e flag
   ```py
   python local_retriever.py -e
   ```
