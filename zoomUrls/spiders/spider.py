import json
import logging
import re
import urllib.parse
from datetime import date
import scrapy
from zoomUrls.items import ZoomurlsItem


class ZoomSpider(scrapy.Spider):
    name = 'zoom_spider'
    allowed_domains = ['hit.ac.il',
                       'zoom.us']
    start_urls = ['https://md.hit.ac.il']

    custom_settings = {
        'DOWNLOAD_DELAY': 0.5,
        'CONCURRENT_REQUESTS': 8,
    }

    # go to login page
    def parse(self, response, **kwargs):
        return scrapy.FormRequest.from_response(response,
                                                formxpath='//form',
                                                callback=self.login_page1
                                                )

    # log in with username and password
    def login_page1(self, response):
        # enter data to moodle's login form
        yield scrapy.FormRequest.from_response(response,
                                               formxpath='//form',
                                               formdata={'Ecom_User_ID': self.username,
                                                         'Ecom_Password': self.password
                                                         },
                                               callback=self.login_page2
                                               )

    # check authentication and redirect
    def login_page2(self, response):
        # authentication failed
        if 'Invalid Credentials' in response.text:
            logging.error("Login failed! - Invalid Credentials")
            return
        else:  # logged in
            print('Logged in to md.hit.ac.il')

        # get redirection url
        redirect = response.xpath('//script/text()').re_first(r'href=[\']?([^\']+)')
        if not redirect:
            logging.error('Could not find redirection url')
            return

        # redirect to the last login page
        yield scrapy.Request(url=redirect, callback=self.login_page3)

    # last login page - enter the csrf token to stay logged in
    def login_page3(self, response):
        # scrape login token
        logintoken = response.xpath('//form/input[@name="logintoken"]/@value').get()

        if not logintoken:
            logging.error('Could not find the csrf token')
            return

        yield scrapy.FormRequest.from_response(response,
                                               formxpath='//form',
                                               formdata={'username': self.username,
                                                         'password': self.password,
                                                         'logintoken': logintoken
                                                         },
                                               callback=self.after_login
                                               )

    def after_login(self, response):
        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.5",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "DNT": "1",
            "Host": "md.hit.ac.il",
            "Pragma": "no-cache",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-User": "?1",
            "Sec-GPC": "1",
            "Upgrade-Insecure-Requests": "1",
        }
        for url in self.urls:
            print(f'Scraping: {url}')
            yield scrapy.Request(url=url, callback=self.getRecPage, headers=headers)

    def getRecPage(self, response):
        url = response.xpath('//li[contains(@class,"lti")]//div[@class="activityinstance"]//a/@href').get()
        if url:
            yield scrapy.Request(url=url, callback=self.parse_form1, headers=response.request.headers)
        elif 'mod/lti/view.php?id' in response.url:
            yield scrapy.Request(url=response.url, callback=self.parse_form1, headers=response.request.headers, dont_filter=True)
        else:
            logging.error('Could not find the recordings page')

    def parse_form1(self, response):
        url = response.xpath('//iframe/@src').get()
        yield response.follow(url, callback=self.parse_form2, headers=response.request.headers)

    def parse_form2(self, response):
        yield scrapy.FormRequest.from_response(response=response, callback=self.parse_form3, headers=response.request.headers)

    def parse_form3(self, response):
        # get the script text from the response
        scriptText = response.xpath('//script/text()').get(default='')
        scriptText = re.findall(r'window.appConf = (.+)', scriptText, re.DOTALL)
        if scriptText:
            scriptText = scriptText[0]
            scriptText = scriptText.replace('\'', '\"')
        else:
            logging.error(f'Could not get "scriptText" in function: \"parse_form3\"')
            return
        # format the text into JSON form
        jsonString = re.sub(r':\s?([a-zA-Z0-9]+)',  r':"\1"', scriptText)              # wrap values
        jsonString = re.sub(r'([a-zA-Z0-9]+):([\{\s\"\'\[])', r'"\1":\2', jsonString)  # wrap keys

        jsonData = json.loads(jsonString)

        headers = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.5",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "application/json;charset=UTF-8",
            "DNT": "1",
            "Host": "applications.zoom.us",
            "Pragma": "no-cache",
            "Referer": "https://applications.zoom.us/lti/rich",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "Sec-GPC": "1",
            "X-KL-Ajax-Request": "Ajax_Request",
        }

        # add the ajax headers to the headers
        headers.update({ajaxHeader['key']: ajaxHeader['value'] for ajaxHeader in jsonData['ajaxHeaders']})

        url = 'https://applications.zoom.us/api/v1/lti/rich/recording/COURSE'
        page = 1

        lti_scid = jsonData['page']['scid']
        lti_scid = urllib.parse.quote(lti_scid)
        payload = f"""startTime=&endTime={date.today().strftime("%Y-%m-%d")}&keyWord=&searchType=1&status=&total=0&lti_scid={lti_scid}"""

        yield scrapy.Request(url=f'{url}?{payload}&page={page}',
                             body=json.dumps(payload),
                             headers=headers,
                             callback=self.parse_urls,
                             cb_kwargs={'url': url,
                                        'payload': payload,
                                        'page': page,
                                        'lti_scid': lti_scid,
                                        'all_meetings': []})

    def parse_urls(self, response, url, payload, page, lti_scid, all_meetings):
        jsonData = response.json()

        if not jsonData['status']:
            logging.error(f'JSON status is false')
            return

        recordingUrl = 'https://applications.zoom.us/api/v1/lti/rich/recording/file?'
        recordingList = jsonData['result']['list']
        if recordingList:

            all_meetings.extend([urllib.parse.quote(meeting['meetingId']) for meeting in recordingList])

            # next page
            page += 1
            yield scrapy.Request(url=f'{url}?{payload}&page={page}',
                                 headers=response.request.headers,
                                 callback=self.parse_urls,
                                 cb_kwargs={'url': url,
                                            'payload': payload,
                                            'page': page,
                                            'lti_scid': lti_scid,
                                            'all_meetings': all_meetings
                                            },
                                 )
        else:
            for meetingId in all_meetings:
                yield scrapy.Request(url=f'{recordingUrl}meetingId={meetingId}&lti_scid={lti_scid}',
                                     headers=response.request.headers,
                                     callback=self.parse_url_page
                                     )

    def parse_url_page(self, response):
        jsonData = response.json()
        if not jsonData['status']:
            logging.error(f"{jsonData['errorMessage']}")
        else:
            item = ZoomurlsItem()
            item['startTime'] = jsonData['result']['startTime']
            for recording in jsonData['result']['recordingFiles']:
                if recording['fileType'] == 'MP4':
                    item['recordingUrl'] = recording['playUrl']
                    yield item
                    print(item)
                    break

# Only for pyinstaller:

import scrapy.utils.misc
import scrapy.core.scraper


def warn_on_generator_with_return_value_stub(spider, callable):
    pass


scrapy.utils.misc.warn_on_generator_with_return_value = warn_on_generator_with_return_value_stub
scrapy.core.scraper.warn_on_generator_with_return_value = warn_on_generator_with_return_value_stub