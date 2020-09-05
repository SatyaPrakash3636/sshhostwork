#! /usr/bin/env python3.8

from fabric import Connection
from json2table import convert
import argparse
import getpass
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import fileinput

parser = argparse.ArgumentParser(
    prog='checkHostViaSSH', description='Description : To verify the access to the server and fetching some details')
parser.add_argument('--version', '-v', action='version',
                    version='%(prog)s 1.0')
parser.add_argument(
    'serverlist', help='Text file containg server list')
parser.add_argument(
    'cmdlist', help='File containing list of commands to execute (one cmd per line)')
parser.add_argument('emailto', help='TO Email ID(Comma separated)')
#parser.add_argument('--cmd', help='Single command to execute')

args = parser.parse_args()
#username = args.username.lower()
emailid = args.emailto


def read_input_file(inputfile):
    """This function returns the list of unique lines from input text file"""
    outlist = []
    with inputfile:
        content = inputfile.read().splitlines()
        #inputnodups = list(set(content))
        for line in content:
            if not line.isspace():
                outlist.append(line.strip())
    return outlist


def html_start():
    with open('output.html', 'w') as f4:
        f4.write('<!DOCTYPE html> <html> <head> <meta name="description" content="Remote command execution Result"> <meta name="author" content="Satyaprakash Prasad"> ')
        f4.write("<style> body { background-color: DarkSlateGray; color: Silver; font-size: 1.1em; } h1 { color: coral; } #intro { font-size: 1.3em; } .colorful { color: orange; } .myTable { width: 100%; text-align: left; background-color: lemonchiffon; border-collapse: collapse; } .myTable th { background-color: goldenrod; color: white; } .myTable td { padding: 2px; border: 1px solid goldenrod; color: black } .myTable th { padding: 2px; border: 1px solid goldenrod; } </style> </head>")
        f4.write('<body>')
        f4.write(
            '<h1>Below are the output of list of commands run against list of hosts</h1>')
        f4.write(
            f'<p id="intro">Note: Kindly verify the output of commands before deciding scope</p>')
        f4.write('<br><br>')


def convert_to_html(data):
    with open('output.html', 'a') as f4:
        build_direction = "TOP_TO_BOTTOM"
        table_attributes = {"class": "myTable"}
        f4.write(convert(data, build_direction=build_direction,
                         table_attributes=table_attributes))
        f4.write('<br><br>')


def html_end():
    with open('output.html', 'a') as f4:
        f4.write('</body> </html>')
    with open('output.html', 'rt') as f4:
        htmldata = f4.read()
        htmldata = htmldata.replace('<ul><li><table', '<table')
        htmldata = htmldata.replace('</table></li></ul>', '</table>')
        htmldata = htmldata.replace('</table></li><li>', '</table>')
    with open('output.html', 'wt') as f4:
        f4.write(htmldata)


def connect_host(hosts, commands, luser, lpass):
    allhostdata = []
    allerrordata = []
    errordata = []
    for host in hosts:
        outdata = []
        with Connection(host=host, port=22, user=luser, connect_timeout='4', connect_kwargs={'password': lpass}) as c:
            for cmd in commands:
                try:
                    result = c.run(cmd, warn=True, hide=True)
                except Exception as loginerror:
                    #print(f"{host} : {loginerror}")
                    cdata = {
                        'Server': host,
                        'Error': loginerror
                    }
                    errordata.append(cdata)
                    errorflag = 1
                    break
                    # allhostdata.append(hostdata)
                    # convert_to_html(hostdata)
                else:
                    fdata = "{}".format(result).split('\n')
                    cdata = {
                        result.command: fdata
                    }
                    outdata.append(cdata)
                    errorflag = 0

        if errorflag == 0:
            hostdata = {
                host: outdata
            }

            allhostdata.append(hostdata)
            convert_to_html(hostdata)
    if errordata:        
        allerrordata = {
            'Servers with error' : errordata
        }
        convert_to_html(allerrordata)
    return allhostdata

# Email defination


def send_email(toaddr, FileName):
    fromaddr = "EAI.Admin.ACN@noreply.com"
    msg = MIMEMultipart('alternative')
    msg['From'] = fromaddr
    msg['To'] = toaddr
    msg['Subject'] = "Remote Execution Result"

    body = open(FileName).read()
    msg.attach(MIMEText(body, 'html'))

    server = smtplib.SMTP('smtp-eu.sanofi.com', 25)
    text = msg.as_string()
    server.sendmail(fromaddr, toaddr.split(','), text)
    server.quit()


def main(username, loginpass):
    print("\nStart of main script.....\n")
    print(f'You have entered username as : {username}\n')
#    print(f'You have entered password as : {loginpass}\n')
#    print(f"calling read_input_file function to read servers from file {args.serverlist}")
    hostlist = read_input_file(f1)
#    print(f'\nRaw host list is :\n\nhostlist = {hostlist}\n')
    if args.cmdlist:
        commandlist = read_input_file(f2)
        #print(f'\nRaw command list is :\n\ncommandlist = {commandlist}\n')
    html_start()
    allhostdata = connect_host(hostlist, commandlist, username, loginpass)
#    print(f'\n\nthis is the the output of commands run against hosts:\n {allhostdata}')
    html_end()
    send_email(emailid, 'output.html')


try:
    f1 = open(args.serverlist)
    if args.cmdlist:
        f2 = open(args.cmdlist)
except Exception as error:
    print(f"Exception : {error}")

else:
    username = input('Enter the username: ')
    if username:
        loginpass = getpass.getpass(prompt='Enter login Password: ')
        if loginpass:
            main(username, loginpass)
        else:
            print('\nNo password provided\n')
    else:
        print('No username provided')
