from queue import SimpleQueue, Empty
import re
import time

from bs4 import BeautifulSoup
import urllib3
from urllib.parse import urljoin


class Node:
    def __init__(self, url, level, father):
        self.url = url
        self.level = level
        self.times_visited = 1
        self.father = father
        self.soup = None


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
    def __init__(self, max_level=1, only_local=True):
        self.http = urllib3.PoolManager(timeout=urllib3.Timeout(connect=5.0, read=5.0))
        self.max_level = max_level
        # If true, the crawler crawls only on the local website.
        self.only_local = only_local
        # Nodes yet to visit.
        self.nodes_queue = SimpleQueue()
        # Visited_nodes has structure {URL, Node}.
        self.visited_nodes = dict()
        # Visited_urls contains strings of URLs already visited.
        self.visited_urls = list()

    def start(self, index_url):
        # Create index node.
        index_node = Node(index_url, 0, None)
        # Add index node to nodes.
        self.nodes_queue.put(index_node)

        end_of_queue = False
        while not end_of_queue:
            try:
                node = self.nodes_queue.get(block=False)
                print("Elements in queue: %d" % self.nodes_queue.qsize())
                self.parse_node(node)
            except Empty:
                end_of_queue = True
                print("End of queue!")
        return

    def parse_node(self, node):
        # Check if I have already visited the node.
        if node.url in self.visited_urls:
            # Node already visited, increment counter, skip visitation.
            self.visited_nodes[node.url].times_visited += 1
            return

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
        node.soup = BeautifulSoup(response.data, 'html5lib')

        print("Visiting %s" % node.url)

        if node.level == self.max_level:
            return

        links = node.soup.find_all('a')

        links = remove_invalid_links(links)

        # Explore all the links in the page.
        for link in links:
            link = link.get("href")
            # Fix link with real address.
            hostname = re.search("^(?:https?://)?(?:[^@/\n]+@)?(?:www\.)?([^:/?\n]+)", node.url)
            link = urljoin(hostname[0], link)

            if self.only_local and not link.startswith(hostname[0]):
                # Skip links redirecting to external websites.
                continue

            # Create a node for each link in the page.
            child_node = Node(link, node.level + 1, node)
            self.nodes_queue.put(child_node)

    def get_most_visited(self):
        nodes = list(self.visited_nodes.values())
        most_visited_nodes = sorted(nodes, key=lambda x: x.times_visited, reverse=True)
        for node in most_visited_nodes[:30]:
            print("Visits: %d - %s - %s" % (node.times_visited, node.soup.title.string, node.url))


start_time = time.time()
crawler = Crawler(2)
crawler.start("https://www.independent.co.uk/")
crawler.get_most_visited()
print("Time elapsed: %.2f s" % (time.time() - start_time))

