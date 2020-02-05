from dotenv import load_dotenv
load_dotenv()
import urllib3
from argparse import ArgumentParser
import exproj
from exproj import db
from passlib.hash import sha256_crypt


def main():
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    parser = ArgumentParser(description='Backend service of Events project')

    # parser.add_argument('role', metavar='role', type=str,
    #                     help='A role of application variant: full backend (full) or RESTful backend (rest)')
    parser.add_argument('--create-tables', type=str, dest='password',
                        help='Creates data base tables before launch.')
    parser.add_argument('--debug', action='store_true', help='Use it for activate debug mode')

    args = parser.parse_args()

    if args.password:
        db.create_tables(sha256_crypt.encrypt(args.password))

    if args.debug:
        exproj.run_debug()
    else:
        exproj.run()


if __name__ == '__main__':
    main()
