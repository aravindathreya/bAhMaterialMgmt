from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select
import time
import random

sampleText = 'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Eget nullam non nisi est sit amet facilisis. Consectetur adipiscing elit duis tristique sollicitudin nibh. Fermentum leo vel orci porta non pulvinar neque laoreet suspendisse. Sed augue lacus viverra vitae congue eu consequat ac felis. Ipsum a arcu cursus vitae congue mauris rhoncus aenean vel. At consectetur lorem donec massa sapien. Accumsan in nisl nisi scelerisque eu ultrices vitae auctor. Habitasse platea dictumst quisque sagittis purus sit amet. Consectetur adipiscing elit ut aliquam purus sit amet luctus venenatis. Sapien nec sagittis aliquam malesuada. Feugiat nibh sed pulvinar proin gravida hendrerit lectus a. Lectus vestibulum mattis ullamcorper velit sed ullamcorper morbi tincidunt ornare. Nullam eget felis eget nunc lobortis. Egestas purus viverra accumsan in nisl. Malesuada proin libero nunc consequat interdum. Sit amet aliquam id diam maecenas. Velit ut tortor pretium viverra suspendisse potenti nullam. Viverra accumsan in nisl nisi scelerisque eu. Sapien pellentesque habitant morbi tristique senectus et netus. '+ \
'Nulla facilisi morbi tempus iaculis. Quis hendrerit dolor magna eget est lorem ipsum dolor. Pellentesque habitant morbi tristique senectus et netus. Et netus et malesuada fames ac. Et malesuada fames ac turpis egestas sed. Morbi blandit cursus risus at ultrices mi tempus. Adipiscing enim eu turpis egestas pretium aenean. Tellus integer feugiat scelerisque varius morbi. Nam aliquam sem et tortor consequat id porta nibh. Faucibus purus in massa tempor nec feugiat nisl pretium fusce. Quis varius quam quisque id diam vel quam elementum pulvinar. Risus ultricies tristique nulla aliquet enim. Lobortis elementum nibh tellus molestie nunc non blandit massa. Eget nullam non nisi est sit.'+ \
'Vel orci porta non pulvinar neque. Luctus accumsan tortor posuere ac ut consequat semper viverra. Nisl vel pretium lectus quam id leo in vitae. Amet nisl purus in mollis nunc. Nulla facilisi etiam dignissim diam quis enim. Sem et tortor consequat id porta nibh venenatis cras sed. Dui accumsan sit amet nulla facilisi morbi tempus. Vitae elementum curabitur vitae nunc sed velit dignissim. Aenean euismod elementum nisi quis eleifend quam adipiscing vitae. Porttitor leo a diam sollicitudin tempor id eu nisl. Scelerisque felis imperdiet proin fermentum leo vel orci porta. Maecenas pharetra convallis posuere morbi leo urna. Metus vulputate eu scelerisque felis imperdiet proin fermentum. Ornare suspendisse sed nisi lacus. Porta non pulvinar neque laoreet suspendisse interdum consectetur. Pulvinar neque laoreet suspendisse interdum consectetur libero id faucibus. Morbi tristique senectus et netus et malesuada fames ac turpis. Tempor orci eu lobortis elementum nibh tellus. In massa tempor nec feugiat nisl pretium. Gravida arcu ac tortor dignissim convallis aenean et tortor at.'+ \
'Hendrerit dolor magna eget est lorem ipsum dolor. Leo a diam sollicitudin tempor id eu nisl nunc mi. Tempus egestas sed sed risus. Felis bibendum ut tristique et egestas quis ipsum suspendisse. Imperdiet dui accumsan sit amet nulla facilisi morbi tempus. Mattis nunc sed blandit libero volutpat sed cras ornare. Sagittis vitae et leo duis ut diam quam nulla porttitor. Metus aliquam eleifend mi in nulla posuere sollicitudin aliquam ultrices. Nisi est sit amet facilisis magna etiam tempor orci eu. Gravida in fermentum et sollicitudin ac orci phasellus. Ut morbi tincidunt augue interdum velit euismod. Vitae auctor eu augue ut lectus arcu bibendum. Amet facilisis magna etiam tempor orci. Sed risus pretium quam vulputate. Lobortis elementum nibh tellus molestie nunc non blandit massa. Diam quis enim lobortis scelerisque fermentum dui. Iaculis nunc sed augue lacus viverra vitae congue eu. Sed id semper risus in hendrerit gravida rutrum. Diam donec adipiscing tristique risus nec feugiat in fermentum posuere. Commodo nulla facilisi nullam vehicula.'
# driver = webdriver.Chrome()
#
# url = driver.command_executor._url
# session_id = driver.session_id
# print(url, session_id)
url='http://localhost:60360'
session_id='02575d57dfddad04fde5098a8c4f376f'
driver = webdriver.Remote(command_executor=url,desired_capabilities={})
driver.close()   # this prevents the dummy browser
driver.session_id = session_id

driver.get('https://app.buildahome.in/enter_material')

material = Select(driver.find_element('name','material'))
material.select_by_index(random.randint(1, len(material.options) -1))

description = driver.find_element('id','description')
sampleDesc = ' '.join(random.sample(sampleText.split(), 5))
description.send_keys(sampleDesc)

vendor = driver.find_element('id','vendor')
sampleVendor = random.choice(sampleText.split())
vendor.send_keys(sampleVendor)

project = Select(driver.find_element('name','project'))
project.select_by_index(random.randint(1, len(project.options) -1))

po_no = driver.find_element('id', 'po_no')
samplePo = str(random.randint(100, 999))
po_no.send_keys(samplePo)

invoice_no = driver.find_element('id', 'invoice_no')
sampleInvoiceNo = random.choice(sampleText.split())+'-'+str(random.randint(100, 999))
invoice_no.send_keys(sampleInvoiceNo)

months = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10','11', '12']
days   = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10','11', '12', '13', '14', '15', '16', '17', '18', '19', '20','21', '22', '23', '24', '25', '26', '27', '28', '29', '30', '31']
years  = ['2008','2009','2010','2011','2012','2013','2014','2015','2016','2017','2018','2019','2020','2021']

rand_date = '{}.{}.{}'.format(*map(random.choice, [months, days, years]))
invoice_date = driver.find_element('id', 'invoice_date')
invoice_date.send_keys(rand_date)

invoice_value = driver.find_element('id', 'invoice_value')
sampleInvoiceValue = (random.randint(10000, 100000) // 1000) * 1000
invoice_value.send_keys(str(sampleInvoiceValue))

quantity = driver.find_element('id', 'quantity')
sampleQuantity = random.randint(10, 50)
quantity.send_keys(str(sampleQuantity))
# time.sleep(5)
# driver.close()