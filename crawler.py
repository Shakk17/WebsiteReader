from queue import SimpleQueue, Empty
import re

from bs4 import BeautifulSoup
import urllib3
from urllib.parse import urljoin


class Node:
    def __init__(self, url, level, father):
        self.url = url
        self.level = level
        self.times_visited = 1
        self.father = father


def remove_invalid_links(links):
    # Find all links that are empty or are anchors to the same page.
    to_be_removed = list()
    for link in links:
        link_href = link.get("href")
        if link_href is None or link_href.startswith('#'):
            to_be_removed.append(link)
    # Remove links just found.
    for link in to_be_removed:
        links.remove(link)
    return links


class Crawler:
    def __init__(self, max_level):
        self.http = urllib3.PoolManager()
        self.max_level = max_level
        # Nodes yet to visit.
        self.nodes = SimpleQueue()
        # Visited_nodes has structure {URL, Node}.
        self.visited_nodes = dict()
        # Visited_urls contains strings of URLs already visited.
        self.visited_urls = list()

    def start(self, index_url):
        # Create index node.
        index_node = Node(index_url, 0, None)
        # Add index node to nodes.
        self.nodes.put(index_node)

        end_of_queue = False
        while not end_of_queue:
            try:
                node = self.nodes.get(block=False)
                print("Elements in queue: %d" % self.nodes.qsize())
                self.parse_node(node)
            except Empty:
                end_of_queue = True
                print("End of queue!")
        return

    def parse_node(self, node):
        # Add node to the list of visited ones.
        self.visited_urls.append(node.url)
        self.visited_nodes[node.url] = node

        # Request page of a node.
        try:
            response = self.http.request('GET', node.url)
        except urllib3.exceptions.MaxRetryError:
            print("Can't access this website: %s" % node.url)
            return
        except urllib3.exceptions.LocationValueError:
            print("Not a valid URL: %s" % node.url)
            return

        # Parse page.
        soup = BeautifulSoup(response.data, 'html5lib')

        print("Visiting %s" % node.url)

        if node.level == self.max_level:
            print("Max depth reached, I'll ignore the links in this page!")
            return

        links = soup.find_all('a')

        links = remove_invalid_links(links)

        # Explore all the links in the page.
        for link in links:
            link = link.get("href")
            # Fix link with real address.
            hostname = re.search("^(?:https?://)?(?:[^@/\n]+@)?(?:www\.)?([^:/?\n]+)", node.url)
            link = urljoin(hostname[0], link)

            # Create a node for each link in the page.
            if link in self.visited_urls:
                # Page already visited, increment counter.
                print("Node already visited. %s" % link)
                self.visited_nodes[link].times_visited += 1
            else:
                # Page not visited yet, create new node.
                child_node = Node(link, node.level + 1, node)
                self.nodes.put(child_node)


crawler = Crawler(2)
crawler.start("http://www.polo-lecco.polimi.it/en/")
