"""
OBJETIVO: 
    - Extraer las opiniones de los usuarios que dejan reviews en hoteles de Cusco en tripadvisor
"""
from scrapy.item import Field
from scrapy.item import Item
from scrapy.spiders import CrawlSpider, Rule
from scrapy.selector import Selector
from scrapy.loader.processors import MapCompose
from scrapy.linkextractors import LinkExtractor
from scrapy.loader import ItemLoader

class Opinion(Item):
  f1_hotel = Field()
  f2_costo = Field()
  f3_cliente = Field()
  f4_titulo = Field()
  f5_contenido = Field()
  f6_calificacion = Field()
  f7_fecHosped = Field()
  f8_page = Field()

class TripAdvisor(CrawlSpider):
  name = 'hotelestripadvisor'
  custom_settings = {
    'USER_AGENT': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 13_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
    'CLOSESPIDER_PAGECOUNT': 100000
  }

  allowed_domains = ['tripadvisor.com']
  start_urls = ['https://www.tripadvisor.com/Hotels-g294314-Cusco_Cusco_Region-Hotels.html']

  download_delay = 2

  rules = (
    Rule( #https://www.tripadvisor.com/Hotels-g294314-Cusco_Cusco_Region-Hotels.html
      LinkExtractor(  # PAGINACION DE HOTELES (HORIZONTALIDAD DE PRIMER NIVEL)
        allow=r'-oa\d+-',
      ), follow=True), # No tiene callback porque aun no voy a extraer datos de aqui. Solamente voy a seguir otras URLs.
    Rule(  # Nueva regla para seguir las páginas de reseñas
        LinkExtractor(
            allow=r'-or\d+-',  # Ajusta el patrón para las páginas de reseñas
        ), follow=True, callback='parse_opinion'),
  
    Rule( 
      LinkExtractor( # DETALLE DE HOTELES (VERTICALIDAD DE PRIMER NIVEL)
        allow=r'/Hotel_Review-', 
        restrict_xpaths=['//*[@class="EJmPL _T e bADWL _T PnJDh"]//a[@class = "BMQDV _F Gv wSSLS SwZTJ FGwzt ukgoS"]'] # Evita obtener URLs repetidas reduciendo el espectro de busqueda de las URLs a solamente un contenedor especifico dentro de un XPATH
      ), follow=True, callback='parse_opinion'), # Aqui si voy a utilizar el callback, debido a que en estas paginas es donde yo quiero extraer datos
  )

  def parse_opinion(self, response):
    sel = Selector(response)
    opiniones = sel.xpath('//div[@data-test-target="reviews-tab"]/div[@class = "YibKl MC R2 Gi z Z BB pBbQr"]') 
    hotel = sel.xpath('//*[@id="HEADING"]/text()').get()
    costo = sel.xpath('//*[@id="DEALS"]//div[@class = "gbXAQ"]/text()').get()
    page = sel.xpath('//*[@id="hrAdWrapper"]//span[@class = "pageNum current disabled"]/text()').get()
    for opinion in opiniones:
      item = ItemLoader(Opinion(), opinion)
      item.add_value('f1_hotel', hotel)
      item.add_value('f2_costo', costo)
      item.add_xpath('f3_cliente', './/a[@class = "ui_header_link uyyBf"]/text()')
      item.add_xpath('f4_titulo','.//div[@class = "KgQgP MC _S b S6 H5 _a"]/a/span/span/text()')
      item.add_xpath('f5_contenido', './/div[@class = "fIrGe _T"]/span/span/text()', MapCompose(lambda i: i.replace('\n', '').replace('\r', '')))
      item.add_xpath('f6_calificacion', './/div[@class = "Hlmiy F1"]/span[contains(@class, "ui_bubble_rating")]/@class', MapCompose(lambda i: i.split('_')[-1]))
      item.add_xpath('f7_fecHosped', './/div[@class = "EftBQ"]/span[1]/text()')
      item.add_value('f8_page', page)
      yield item.load_item()

# EJECUCION EN TERMINAL
# scrapy runspider 1_tripadvisor_hoteles_cusco.py -o tripadvisor_hoteles_cusco.csv -t csv