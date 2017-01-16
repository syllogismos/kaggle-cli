from cliff.command import Command
import shutil
from . import common

class Download(Command):
    'Download data files from a specific competition.'

    def get_parser(self, prog_name):
        parser = super(Download, self).get_parser(prog_name)

        parser.add_argument('-c', '--competition', help='competition')
        parser.add_argument('-u', '--username', help='username')
        parser.add_argument('-p', '--password', help='password')
	parser.add_argument('-f', '--filename', help='filename')

        return parser

    def take_action(self, parsed_args):
        (username, password, competition) = common.get_config(parsed_args)
        browser = common.login(username, password)
	file_name = parsed_args.filename

        base = 'https://www.kaggle.com'
        data_url = '/'.join([base, 'c', competition, 'data'])

        data_page = browser.get(data_url)
        links = data_page.soup.find(id='data-files').find_all('a')

        for link in links:
	    if file_name == None or link.get('name') == file_name:
	        print link
	        print file_name
                url = base + link.get('href')
                self.download_file(browser, url)

    def download_file(self, browser, url):
        self.app.stdout.write('downloading %s\n' % url)
        local_filename = url.split('/')[-1]
        stream = browser.get(url, stream=True)
        if not self.is_html_response(stream):
            warning = ("Warning: download url for file %s resolves to an html document rather than a downloadable file. \n"
                        "See the downloaded file for details. Is it possible you have not accepted the competition's rules on the kaggle website?") % local_filename
            self.app.stdout.write(warning+"\n")
        with open(local_filename, 'wb') as f:
            for chunk in stream.iter_content(chunk_size=1024): 
                if chunk: # filter out keep-alive new chunks
                    f.write(chunk)

    def is_html_response(self, response):
        """
        Checks whether the response object is a html page or a likely downloadable file.
        Intended to detect error pages or prompts such as kaggle's competition rules acceptance prompt.

        Returns True if the response is a html page. False otherwise.
        """
        content_type = response.headers.get('Content-Type', "")
        content_disp = response.headers.get('Content-Disposition', "")
        if "text/html" in content_type and not "attachment" in content_disp:
            # This response is a html file which is not marked as an attachment,
            # so we likely hit a rules acceptance prompt
            return False
        return True
