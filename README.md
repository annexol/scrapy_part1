# Test task scrapy part1

git_spider parses and saves the following data to the database:
a. Repository name
b. Description
c. Link
d. Number of stars
e. Number of forks
f. Number of watchers
g. Number of commits
h. Information about the last commit 
i. Number of releases
j. Information about the latest release 

### Installation process

<pre>
mkdir test_task_scrapy && cd test_task_scrapy && \
git clone https://github.com/annexol/scrapy_part1.git
</pre>

After opening the project(scrapy_part1) you need to run the commands in the terminal

<pre>
pip install -r requirements.txt
cd scrapy_task
scrapy crawl git_spider
</pre>
### Guideline

In the file .../spiders/git_spider.py you need to put the list of links in start_urls

<pre>
 start_urls = ['https://github.com/example1', 'https://github.com/example2']
</pre>


...after to run the command in the terminal...

<pre>
scrapy crawl git_spider
</pre>


Data is saved to mongodb database. In the file .../spiders/data_base.py you can set the name of the database and the name of the collection


<pre>
    current_db = db_client["db_name"]
    collection = current_db["collection_name"]
</pre>




