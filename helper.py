import tldextract
from databases.database_handler import Database


class Helper:
    def get_menu(self, url):
        """
        Analyze the scraped pages from the url's domain, then returns the 10 most frequent links.
        Returns a list of tuples (text, url) corresponding to the anchors present in the menu.
        """
        extracted_domain = tldextract.extract(url)
        domain = "{}.{}".format(extracted_domain.domain, extracted_domain.suffix)
        menu = Database().analyze_scraping(domain)
        return menu

    def go_to_section(self, url, name=None, number=None):
        """
        Given the name of one of the menu's entries, returns its URL.
        """
        # Get menu.
        menu = self.get_menu(url)
        menu_strings = [tup[0] for tup in menu]
        menu_anchors = [tup[1] for tup in menu]

        # Check if the parameter is the name of the section or the index.
        if name is not None:
            # Put all the strings to lowercase.
            menu_strings = [string.lower() for string in menu_strings]
            # Return index of string, if present. Otherwise, IndexError.
            index = menu_strings.index(name.lower())
        else:
            index = number

        return menu_anchors[index]
