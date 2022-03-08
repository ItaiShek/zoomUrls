import sys
import os
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from new_parser import NewParser, NewHelpFormatter


def get_custom_settings(arguments):
    s = {}
    if arguments.verbose:
        s['LOG_LEVEL'] = 'DEBUG'
    if arguments.user_agent:
        s['USER_AGENT'] = arguments.user_agent
    if arguments.output:
        if not arguments.output.lower().endswith('.csv'):
            arguments.output += '.csv'
        s['FEEDS'] = {f'{arguments.output}': {'format': 'csv', 'fields': ['startTime', 'recordingUrl']}}
    return s


def main():
    parser = NewParser(
        description='Get all zoom recording urls from md.hit.ac.il course/s',
        usage='zoomUrls -u USERNAME -p PASSWORD URL [URL1 URL2...]\n\n'
              ' e.g.: zoomUrls -u student -p pass123 https://md.hit.ac.il/course/view.php?id=12345',
        formatter_class=lambda prog: NewHelpFormatter(prog, max_help_position=27)
    )

    parser.add_argument('-u', '--username', metavar='', required=True, help="Your moodle username")
    parser.add_argument('-p', '--password', metavar='', required=True, help="Your moodle password")
    parser.add_argument('URL', nargs='+', help="The course/s url/s you want to scrape")
    parser.add_argument('-v', '--verbose', action='store_true', help='Print debugging information')
    parser.add_argument('-o', '--output', metavar='', help='Save the urls to a csv file')
    parser.add_argument('-a', '--user-agent', metavar='', help='Override the default user agent')

    if len(sys.argv) <= 1:
        parser.print_help()
        sys.exit(0)

    args = parser.parse_args()

    # set user settings
    custom_settings = get_custom_settings(args)

    # start crawling
    # the next two lines are only for pyinstaller
    settings_file_path = 'settings'
    os.environ.setdefault('SCRAPY_SETTINGS_MODULE', settings_file_path)

    settings = get_project_settings()
    settings.update(custom_settings)
    process = CrawlerProcess(settings)

    process.crawl('zoom_spider', username=args.username, password=args.password, urls=args.URL)
    process.start()
    print("\n\nFinished")
    sys.exit(0)


if __name__ == '__main__':
    main()
