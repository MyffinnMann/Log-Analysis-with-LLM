# Set up NGINX as reverse proxy with encryption using a selfsigned certificate

## Requirements and prerequisites

1. To be able to follow the guide make sure that you are using either Debian or Ubuntu. It is possible to run nginx on other systems but paths and package names might differ.

2. Make sure the following software packages are installed
    - nginx
    - openssl

    On Debian/Ubuntu run
    ```
    apt-get install nginx openssl
    ```

3. Make sure that you are logged into the root account. If unsure what account you are using run `whoami`, which would return root if the current terminal is logged in as root. To change the current terminal to be logged in as root run

    ```
    sudo su
    ```
    
    and enter the current logged in user's password. Then run `whoami` to check if you are logged in as root.


## Selfsigned certificate

To use HTTPS you have to have a certficate. For offline testing we are going to generate and use a selfsigned certificate. To generate the selfsigned certificate, two files will be generated using openssl.

For simplicity's sake create a directory in `/etc/nginx` called `ssl`. Then change to that directory

```
mkdir /etc/nginx/ssl
cd /etc/nginx/ssl
```

To generate a selfsigned certificate use the following command

```
openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout securelanglogs.key -out securelanglogs.crt
```

Press enter for all questions, except the common name, there enter securelanglogs.net

If everything to this point has been done correctly two files named `securelanglogs.pem` and `securelanglogs.pem` has been created in `/etc/nginx/ssl`.

To check this run.

```
ls /etc/nginx/ssl
```

## Nginx as a reverse proxy

To serve the web page we are going to use Nginx as a reverse proxy for receiving and forwarding everything to and from Flask.

If the install of nginx is fresh, remove the default server

```
rm /etc/nginx/sites-enabled/default
```

then create a new file in `/etc/nginx/sites-available` called `securelanglogs`.


```
touch /etc/nginx/sites-availble/securelanglogs
```

Open the file and paste the following server config into the file using a preferred text edit such as vim, nano, etc.

```
server {
        listen 443 ssl;
        listen [::]:443 ssl;

        ssl_certificate /etc/nginx/ssl/securelanglogs.crt;
        ssl_certificate_key /etc/nginx/ssl/securelanglogs.key;

        server_name securelanglogs.net;

        location / {
                proxy_pass http://127.0.0.1:5000;
                proxy_set_header Host $host;
                proxy_set_header X-Real-IP $remote_addr;
                proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
                proxy_set_header X-Forwarded-Proto $scheme;
        }
}

server {
        listen 80;
        listen [::]:80;

        server_name securelanglogs.net;
        if ($host = securelanglogs.net){
                return 301 https://$host$request_uri;
        }
}
```

Edit the line starting with `proxy_pass` to the contain the actual ip where the flask api is hosted. 127.0.0.1 if hosting everything on Linux, and the IP-address of the Windows host address if nginx is running in WSL.

Save the file and create a symlink from the newly created file to the directory `/etc/nginx/sites-enabled/`

```
ln -s /etc/nginx/sites-availble/securelanglogs /etc/nginx/sites-enabled/
```

Then restart nginx using

```
systemctl restart nginx
```

## Set up the domain

To connect to the server we are going to use the domain name `securelanglogs.net`. To be able use the domain you will have to edit the `hosts` file on the computer you are going to connect to the web server from. The `hosts` file is a table which maps domains to ip addresses, which is what DNS does but in this case locally.

Locate the hosts file.
- Linux: `/etc/hosts` 
- Windows: `C:\Windows\system32\drivers\etc\hosts`

Then open the file using root on Linux, or administrative privileges on Windows.

If you are using Linux for testing add the following to the the last line of the file. 

```
127.0.0.1   securelanglogs.net
```

If you are using WSL for hosting find the ip address of the WSL installation, and then replace `127.0.0.1` with the IP address of the WSL installation.

Try to ping the domain, if `127.0.0.1` or the WSL installations IP adress responds it worked.


## Test

Everything should be working at this stage. Try to connect to `securelanglogs.net` in a web browser and accept that you are using a selfsigned certificate.

If it is not working start troubleshooting.

### Troubleshooting

- Check if the ip address is right.
- Check if nginx is running.
    - `systemctl status nginx`. If it says running, try next step.
- Check if all the IP addresses configured are correct.
- Ping the IPs configured.
- Check if everything is running.
- Try using another web browser.
- Restart computer.
- Check if the changes were saved in the `hosts` file.
- ...
