import scrapy
import pandas as pd
import time
class FilimoSpider(scrapy.Spider):
    name = 'filimo'
    allowed_domains = ['filimo.com']
    base_url = 'https://www.filimo.com/cms/movie/loadmore/tagid/1001/more_type/infinity/show_serial_parent/1/perpage/8/page/1'
    start_urls = [base_url]
    df = pd.DataFrame(columns = ['name_en', 'name_fa','director' ,
            'imdb', 'overal_rate', 'rates_count', 'episodes_rates', 'link'])
    df.to_csv('rates.csv', encoding= 'utf-8', mode = 'w')
    def parse(self, response):
        links =  response.css('div.fs-body-2 ::attr(href)').extract()
        # name = response.css('div.fs-body-2 > a ::text').extract()
        for link in links:
            yield scrapy.Request(link, self.parse_rate )
            time.sleep(0.2)
        # df = pd.DataFrame({'name': name, 'links':links})
        # df.to_csv('movie_list.csv', mode='a', header = False)
        button = response.css('button.request-link ::attr(data-href)').extract()
        
        if len(button)>0:
            yield scrapy.Request(button[0], self.parse)
            time.sleep(0.2)

    def parse_rate(self, response):
        rates = response.css('div.accordion > li.accordion-item > div.accordion-top > div.right > span.episode-rate > span.percent ::text').extract()
        name_fa = response.css('h1.movie-title>span.fa::text').extract()
        name_en = response.css('h1.movie-title>span.en::text').extract()
        name_fa = [' '.join(name_fa)]
        if len(name_en) == 0:
            name_en = ['NaN']

        overall_rate = response.css('div.rating-wrapper > div.ds-badge > span.ds-badge_label > span[id] ::text').extract()
        rates_count = response.css('div.rating-wrapper > div.ds-badge > span.ds-badge_label > span.total-number > span[id] ::text').extract()
        imdb_rate = response.css('div.rating-wrapper > div.ds-badge > span.ds-badge_label > span.en ::text').extract()
        
        movie_director = response.css('div.mobile-wrapper > div.meta-wrapper > div.movie-director > a ::text').extract()
        movie_director = [', '.join(movie_director)]
        if len(imdb_rate)==0 :
            imdb_rate = ['NaN']
        else :
            imdb_rate = [imdb_rate[0]]
        self.log('=============={},  {}, {}, {}'.format(str(len(overall_rate)),str(len(rates_count)),str(len(imdb_rate)),str(len(movie_director))))
        rate_df = pd.DataFrame({'name_en':name_en, 'name_fa': name_fa,'director':movie_director ,
            'imdb': imdb_rate, 'overal_rate': overall_rate, 'rates_count': rates_count, 'episodes_rates':list([rates]), 'link':[response.url]})
        rate_df.to_csv('rates.csv', encoding='utf-8', header = False, mode = 'a')
