pip install -r build_requirements.txt
pyinstaller randomizer.pyw
xcopy files dist\randomizer\files /e /i
copy assets\d2rand.exe dist\
move dist d2rand
