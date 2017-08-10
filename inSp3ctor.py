#!/usr/bin/env python2.7

from awsauth import S3Auth
from bs4 import BeautifulSoup
from colorama import init, Fore, Back, Style
import argparse
import requests
import urllib
import sys

def parse_response(xml_response):
    """ Get the content of the HTML page for the bucket and return
    the redirected page if given a 301 status

    Args:
        xml_response (str): The HTML content from an s3 bucket

    Returns:
        String of the redirected S3 bucket
    """
    y = BeautifulSoup(xml_response, "html.parser")
    return y.error.endpoint.string

def check_object_status(xml_response, site):
    """ Get the content of the HTML page for the bucket and return
    the status of objects contained in the bucket

    Args:
        xml_response (str): The HTML content from an s3 bucket

    Returns:
        Object status
    """
    y = BeautifulSoup(xml_response, "html.parser")
    object_keys = y.findAll('key')
    for key in object_keys:
        bucket_checker(site + "/" + key.get_text(),"Object")


def check_response(status_code, word, content, s3_type):
    """ Formats the response code based on status code returned
    from s3 bucket, and changes color depending on the response.

    Args:
        status_code (int): The HTTP response code from the s3 bucket
        word (str): The name of the s3 bucket to check
        content (str): The HTML content from the s3 bucket

    Returns:
        None
    """
    if args.s:
        if status_code == 200:
            print (Back.GREEN + '[*] ' + s3_type + ' is public [' +
                    word.rstrip() + ']' + Style.RESET_ALL)
            if args.o:
                check_object_status(content, word)
    else:
        if status_code == 200:
            print (Back.GREEN + '[*] ' + s3_type + ' is public [' +
                        word.rstrip() + ']' + Style.RESET_ALL)
            if args.o:
                check_object_status(content, word)
        elif status_code == 403:
            print (Back.YELLOW + '[!] ' + s3_type + ' is marked private [' +
                        word.rstrip() + ']' + Style.RESET_ALL)
        elif status_code == 301:
            print (Back.RED + '[>] ' + s3_type + ' has a redirect [' +
                        word.rstrip() + '] Redirected here - [' +
                        parse_response(content) + ']' + Style.RESET_ALL)
        else:
            print '[-] ' + s3_type + ' does not exist or cannot list [' + word.rstrip() + ']'


def print_header():
    """ Prints a formatted header

    Args:
        None

    Returns:
        None
    """
    print Style.RESET_ALL + Fore.WHITE + Back.BLUE
    print " ".ljust(80)
    print "   _      ____     ____     __          ".ljust(80)
    print "  (_)__  / __/__  |_  /____/ /____  ____".ljust(80)
    print " / / _ \_\ \/ _ \_/_ </ __/ __/ _ \/ __/".ljust(80)
    print "/_/_//_/___/ .__/____/\__/\__/\___/_/   ".ljust(80)
    print "          /_/     ".ljust(80)
    print " ".ljust(80)
    print "  AWS S3 Bucket Finder                        ".ljust(80)
    print "  Brian Warehime @nullsecure".ljust(80)
    print " ".ljust(80) + Style.RESET_ALL
    print " "


def bucket_checker(word, s3_type):
    """ Grabs the response from the bucket and checks the response code
    to determine if the bucket is public or private

    Args:
        word (str): The bucket name to check

    Returns:
        None
    """
    if s3_type == "Object":
        if args.a:
            checker = requests.head(word.rstrip(), auth=S3Auth(ACCESS_KEY, SECRET_KEY))
        else:
            checker = requests.head(word.rstrip())
    if s3_type == "Bucket":
        if args.a:
            checker = requests.get(word.rstrip(), auth=S3Auth(ACCESS_KEY, SECRET_KEY))
        else:
            checker = requests.get(word.rstrip())
    response = check_response(checker.status_code, word, checker.content, s3_type)


def grab_wordlist(inputfile):
    """ Grabs each line of a given wordlist

    Args:
        inputfile (str): The name of the text file with bucket names

    Returns:
        None
    """
    with open(inputfile) as f:
        for line in f:
            bucket_checker(line, "Bucket")

def add_permutations(word):
    """ Given a root word, append a permutation of common terms to view
    if they are created or not.

    Args:
        word (str): The root word to append permutations to

    Returns:
        None
    """
    with open('permutations.txt') as f:
        for line in f:
            bucket_checker("http://" + word + line.rstrip() + ".s3.amazonaws.com","Bucket")
            bucket_checker("http://s3.amazonaws.com/" + word + line.rstrip(),"Bucket")


if __name__ == '__main__':

    print_header()

    parser = argparse.ArgumentParser(description='AWS s3 Bucket Permutation Checker')
    parser.add_argument('-w', help='Specify explicit wordlist to use for all bucket checking', metavar='wordlist', default='')
    parser.add_argument('-n', help='Specify the root name to use, i.e. google, amazon', metavar='root', default='')
    parser.add_argument('-o', help='Check objects in a public s3 bucket if they are available', action='store_true')
    parser.add_argument('-a', help='Use AWS Credentials to authenticate the request', action='store_true')
    parser.add_argument('-s', help='Only show buckets/objects that are public in the results', action='store_true')
    args = parser.parse_args()

    if args.a:
        ACCESS_KEY = ''
        SECRET_KEY = ''
        if len(ACCESS_KEY) == 0:
            print "[!] Need to supply ACCESS_KEY and SECRET_KEY in this file."
            sys.exit(1)

    if not args.n and not args.w:
        print "[!] Need to specify root name to use"
        parser.print_help()
        sys.exit(1)

    if args.w:
        print "[!] Reading s3 bucket names from " + args.w
        grab_wordlist(args.w)

    if args.n:
        print "[!] Applying permutations to " + args.n
        add_permutations(args.n)
