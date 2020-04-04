from dotenv import load_dotenv
load_dotenv()
import urllib3
from argparse import ArgumentParser
import bcrypt

import exproj
from exproj import db


def main():
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    parser = ArgumentParser(description='Backend service of Events project')

    parser.add_argument('--create-tables', type=str, dest='password',
                        help='Creates data base tables before launch.')

    parser.add_argument('--debug', action='store_true',
                        help='Use it for activate debug mode')

    args = parser.parse_args()

    if args.password:
        pw = bcrypt.hashpw(str(args.password).encode('utf-8'), bcrypt.gensalt())
        db.create_tables(pw.decode('utf-8'))

    if args.debug:
        exproj.run_debug()
    else:
        exproj.run()


if __name__ == '__main__':
    main()
