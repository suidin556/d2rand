pip install -r requirements.txt
pyinstaller randomizer.pyw
xcopy files dist\randomizer\files /e /i
copy assets\d2rand.exe dist\
move dist d2rand
powershell -Command "Compress-Archive d2rand d2rand.zip"
