import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy.utils.log import configure_logging
from twisted.internet import reactor
from scrapy.crawler import CrawlerRunner
import maya
from .data_base import *


class GitSpiderSpider(CrawlSpider):
    download_delay = 0.8
    name = 'git_spider'
    allowed_domains = ['github.com']
    start_urls = ['https://github.com/scrapy', 'https://github.com/annexol', 'https://github.com/celery',
                  'https://github.com/blackholll', 'https://github.com/Oliver0047', 'https://github.com/ppy2790',
                  'https://github.com/zepen', 'https://github.com/Henryhaohao']

    rules = (
        Rule(
            LinkExtractor(allow='repositories'), follow=True),
        Rule(
            LinkExtractor(restrict_xpaths='//h3[@class = "wb-break-all"]/a'),
            callback='parse_pages', follow=True),
        Rule(
            LinkExtractor(restrict_xpaths='//a[@class = "next_page"]'), follow=True),

    )

    def parse_pages(self, response):
        item = {}
        item['name'] = response.xpath('//span[@class = "author flex-self-stretch"]/a/text()').get().replace("'", "`")
        item['repository_name'] = response.xpath(
            '//a[@data-pjax = "#repo-content-pjax-container"]/text()').get().replace("'", "`")
        try:
            item['about'] = response.xpath('//p[@class = "f4 my-3"]/text()').get().strip().replace("'", "`")
        except Exception as e:
            item['about'] = None

        item['site'] = response.xpath(
            '//span[@class = "flex-auto min-width-0 css-truncate css-truncate-target width-fit"]/a/@href').get()
        item['stars'] = int(response.xpath(
            '//span[@id = "repo-stars-counter-star"]/@aria-label').get().split()[0])
        item['forks'] = int(response.xpath(
            '//span[@id = "repo-network-counter"]/@title').get().replace(',', ''))

        watchers = response.xpath(
            '//div[@class="mt-2"]/a/strong/text()').getall()[1]
        if '.' in watchers:
            item['watchers'] = int(watchers.replace('.', '').replace('k', '')) * 100
        elif 'k' in watchers:
            item['watchers'] = int(watchers.replace('k', '')) * 1000
        else:
            item['watchers'] = int(watchers)

        item['commits_number'] = int(response.xpath(
            '//span[@class="d-none d-sm-inline"]/strong/text()').get().replace(',', ''))
        item['releases_number'] = int(response.xpath(
            '//h2[@class="h4 mb-3"]/a/span/text()').getall()[0])
        item['release_version'] = None
        item['release_date'] = None
        item['release_changelog'] = None
        item['link_commit'] = response.xpath(
            '//div[@class="flex-shrink-0"]/ul/li/a/@href').get()
        item['link_realises'] = response.xpath(
            '//div[@class = "BorderGrid-cell"]/a[@class = "Link--primary d-flex no-underline"]/@href').get()

        return response.follow(item['link_commit'], self.commits, cb_kwargs=dict(item=item))

    def realises(self, response, item):
        item['release_version'] = response.xpath('//div[@class = "flex-1"]/h1/text()').get().replace("'", "`")
        try:
            item['release_date'] = maya.parse(
                response.xpath('//div[@class = "mr-4 mb-2"]/local-time/@datetime').get()).datetime()
        except Exception as e:
            item['release_date'] = maya.parse(
                response.xpath('//div[@class = "mr-4 mb-2"]/relative-time/@datetime').get()).datetime()

        text_html = response.xpath('//div[@class = "markdown-body my-3"]').getall()

        item['release_changelog'] = self.filter_text(text_html)
        name = item['name']
        [item.pop(key) for key in ['link_commit', 'link_realises', 'name']]
        insert_db(item, name)

    def commits(self, response, item):
        item['commit_author'] = response.xpath(
            '//a[@class="commit-author user-mention"]/text()').get().replace("'", "`")
        item['commit_name'] = response.xpath(
            '//a[@class="Link--primary text-bold js-navigation-open markdown-title"]/text()').get().replace("'", "`")
        item['commit_date'] = maya.parse(response.xpath(
            '//div[@class="f6 color-fg-muted min-width-0"]/relative-time/@datetime').get()).datetime()

        if item['link_realises']:
            return response.follow(item['link_realises'], self.realises, cb_kwargs=dict(item=item))
        else:
            name = item['name']
            [item.pop(key) for key in ['link_commit', 'link_realises', 'name']]
            insert_db(item, name)

    @staticmethod
    def filter_text(html_text):
        text = '\n'.join(html_text)
        tags = []
        temp_tag = ''

        for i in text:
            if i == '<':
                temp_tag = ''
                temp_tag += i
                continue
            if i == '>':
                temp_tag += i
                tags.append(temp_tag)
                temp_tag = ''
                continue
            temp_tag += i
        for tag in set(tags):
            text = text.replace(tag, '')
        text = text.replace("'", "`")

        return text

# configure_logging()
# runner = CrawlerRunner()
# runner.crawl(GitSpiderSpider)
# d = runner.join()
# d.addBoth(lambda _: reactor.stop())
#
# reactor.run()  # the script will block here until all crawling jobs are finished
