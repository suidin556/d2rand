> This project will not be updated anymore.
> Please check out [D2Modmaker](https://github.com/tlentz/d2modmaker), an active and more feature rich tool for diablo2 randomization/modding


# Randomizer tool for Diablo II
This is a tool to randomize and alter various values of Diablo II by using its build-in modding capabilities.
It doesn't change any game files. Only a "data" folder with the modified .txt files will be created and copied to the specified Diablo II folder.
Make sure there are no important files in your data/global/excel/ folder, because that folder will be deleted before every randomization (based on your choosen Diablo Path).

## Starting d2rand
Windows builds can be found under [Releases](https://github.com/suidin556/d2rand/releases) and will not always be up to date.
If you have Python installed, you can always just run the newest version:
```
pip install -r requirements.txt
python randomizer.pyw
```

## Building
Make sure you have installed Python3 from the windows installer, which will also install PIP along with it.
You also need to have those tools in your windows path (there is a checkbox for that during the python installation).
Then just run the "build.bat", which will create a "d2rand" folder with the executables.
