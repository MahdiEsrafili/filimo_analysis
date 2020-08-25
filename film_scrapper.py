import scrapy
import pandas as pd
import time
import re
class FilmScrapperSpider(scrapy.Spider):
    name = 'film_scrapper'
    allowed_domains = ['filimo.com']
    start_urls = ['https://www.filimo.com/movies']
    # df = pd.DataFrame(columns = ['name', 'links'])
    # df.to_csv('films_list.csv', encoding= 'utf-8', mode = 'w')
    rate_df = pd.DataFrame(columns = ['name_en', 'name_fa','director' ,
            'imdb', 'overal_rate', 'rates_count','comment_name' ,
            'comment_date', 'comment_likes', 'comment_dislikes',
            'comment_text', 'link', 'comment_page_link'])

    rate_df.to_csv('serial_rates.csv', encoding= 'utf-8', mode = 'w')
    def parse(self, response):
        links =  response.css('div.fs-body-2 ::attr(href)').extract()
        name = response.css('div.fs-body-2 > a ::text').extract()
        for link in links:
            yield scrapy.Request(link, self.parse_film )
            time.sleep(0.2)
        # df = pd.DataFrame({'name': name, 'links':links})
        # df.to_csv('films_list.csv', mode='a', header = False)
        button = response.css('button.request-link ::attr(data-href)').extract()
        
        if len(button)>0:
            yield scrapy.Request(button[0], self.parse)
            time.sleep(0.2)

    def parse_film(self, response):
        self.log(response.meta)
        if 'name_fa' in response.meta.keys():
            name_fa = response.meta['name_fa'][0],
            name_en = response.meta['name_en'][0],
            overall_rate = response.meta['overall_rate'][0],
            rates_count = response.meta['rates_count'][0],
            imdb_rate = response.meta['imdb_rate'][0],
            movie_director = response.meta['movie_director'][0],
            req_url = [response.meta['url'][0]]
            self.log('======from meta {}'.format(overall_rate))

        else:
            name_fa = response.css('h1.movie-title>span.fa::text').extract()
            name_fa = [' '.join(name_fa)]
            name_fa = [re.sub('\s\s', '', name_fa[0])]
            name_en = response.css('h1.movie-title>span.en::text').extract()
            
            if len(name_en) == 0:
                name_en = ['NaN']

            overall_rate = response.css('div.rating-wrapper > div.ds-badge > span.ds-badge_label > span[id] ::text').extract()
            rates_count = response.css('div.rating-wrapper > div.ds-badge > span.ds-badge_label > span.total-number > span[id] ::text').extract()
            imdb_rate = response.css('div.rating-wrapper > div.ds-badge > span.ds-badge_label > span.en ::text').extract()
            movie_director = response.css('div.mobile-wrapper > div.meta-wrapper > div.movie-director > a ::text').extract()
            movie_director = [', '.join(movie_director)]
            req_url = [response.url]

            if len(imdb_rate)==0 :
                imdb_rate = ['NaN']
            else :
                imdb_rate = [imdb_rate[0]]

        comment_item = response.css('ul.comment-list > li.comment-item')
        comment_name_list = []
        comment_date_list = []
        comment_likes_list = []
        comment_dislikes_list = []
        comment_text_list = []
        comment_page_link = []

        for item in comment_item:
            comment_name = item.css('div.comment-left-side > div.comment-info > span.comment-name ::text').extract()
            comment_date = item.css('div.comment-left-side > div.comment-info > span.comment-date ::text').extract()
            comment_likes = item.css('div.comment-left-side > div.comment-info > div.rate > span.like > button.thumbs-up > i.like-count::text').extract()
            comment_dislikes = item.css('div.comment-left-side > div.comment-info > div.rate > span.like > button.thumbs-down > i.like-count::text').extract()
            comment_text = item.css('div.comment-left-side > div.comment-body > p.comment-content::text').extract()
            comment_text = [re.sub('(\t|\n)','',comment_text[0] )]
            comment_page = [response.url]
            
            if len(comment_likes) ==0:
                comment_likes = ['NaN']
                comment_dislikes = ['NaN']
            comment_name_list.append(comment_name[0])
            comment_date_list.append(comment_date[0])
            comment_likes_list.append(comment_likes[0])
            comment_dislikes_list.append(comment_dislikes[0])
            comment_text_list.append(comment_text[0])
            comment_page_link.append(comment_page)
        
        if len(comment_name_list) == 0:
            comment_name_list= ['NaN']
            comment_date_list= ['NaN']
            comment_likes_list= ['NaN']
            comment_dislikes_list= ['NaN']
            comment_text_list= ['NaN']
            comment_page_link = ['NaN']

        main_rates = {
            'name_fa' : name_fa,
            'name_en' : name_en,
            'overall_rate' : overall_rate,
            'rates_count' : rates_count,
            'imdb_rate' : imdb_rate,
            'movie_director' : movie_director,
            'url' : req_url
        }    

        name_fa = name_fa * len(comment_name_list)
        name_en = name_en * len(comment_name_list)
        overall_rate = overall_rate * len(comment_name_list)
        rates_count = rates_count * len(comment_name_list)
        imdb_rate = imdb_rate * len(comment_name_list)
        movie_director = movie_director * len(comment_name_list)
        
        self.log('=================={}, {}, {}, {}, {}, {}, {},'.format(str(len(comment_name_list)),
            str(len(comment_date_list)),str(len(comment_likes_list)),
            str(len(comment_dislikes_list)),str(len(comment_text_list)),
            str(len(name_fa)),str(len(overall_rate)),))

        response.css('div.loadmore-link > button.comments-loadmore ::attr(data-href)').extract()
        rate_df = pd.DataFrame({'name_en':name_en, 'name_fa': name_fa,'director':movie_director ,
            'imdb': imdb_rate, 'overal_rate': overall_rate, 'rates_count': rates_count, 'comment_name':comment_name_list ,
            'comment_date':comment_date_list, 'comment_likes':comment_likes_list, 'comment_dislikes':comment_dislikes_list,
            'comment_text':comment_text_list,  'link':req_url*len(comment_name_list), 'comment_page_link':comment_page_link})
        rate_df.to_csv('film_rates.csv', encoding='utf-8', header = False, mode = 'a')

        load_more = response.css('div.loadmore-link > button.comments-loadmore ::attr(data-href)').extract()
        if len(load_more) > 0:
            yield scrapy.Request(load_more[0], self.parse_film, meta= main_rates )
            time.sleep(0.2)