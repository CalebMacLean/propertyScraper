import re

class Parser:
    """Parsing Class for finding data"""

    def __init__(self) -> None:
        pass
    
    @classmethod
    def find_owner_info_by_header(header_name, th_iterable):
        """Finds element with relevant data by using the table head in the row"""
        # Takes th soup iterable, and isolates one th at a time.
        for header in th_iterable:
            # Accesses the current th's contents.
            for content in header.contents:
                # Checks that contents are a string and match the given header name.
                if (content.string is not None) and (content.string.strip().lower() == header_name.lower()):
                    # Returns the actual owner data element that is in the same row.
                    return header.next_sibling.next_sibling
            else:
                continue
        # Case: Couldn't find header or owner data element.
        return None

    @classmethod
    def get_owner_data(cls, header_name, th_iterable):
        """Retrieves data"""
        # Case for Searching for Situs 1
        if(header_name.lower() == 'situs 1') or (header_name.lower() in 'situs 1'):
            # Locates Parcel's address element.
            element = cls.find_owner_info_by_header('situs 1', th_iterable)
            # Creates and Returns list of elements relevant strings.
            return " ".join([string.strip() for string in element.strings])
    
        # Case for Searching for Owner
        if (header_name.lower() == 'owner 1') or (header_name.lower() in 'owner 1'):
            # Locates and returns Parcel's owner's name element.
            element = cls.find_owner_info_by_header('owner 1', th_iterable)
            return element.string.strip()
    
        # Case for Searching for Mail Address
        if (header_name.lower() == 'mail address') or (header_name.lower() in 'mail address'):
            # Locates Parcel's owner's mail address element.
            element = cls.find_owner_info_by_header('mail address', th_iterable)
            # Creates list of element's relevant strings, but they are very messy and need to be cleaned up.
            result = [string.replace('\xa0\xa0\n', '').strip() for string in element.strings if string.strip() != '']
            # Checks that the second string made it to the list.
            if result[1]:
                # If second string it needs to be modified to be less janky.
                result[1] = re.sub(' +', ' ', result[1])
        
            return " ".join(result)


    @classmethod
    def get_sales_data(spans):
        """
        Uses Soup span iterable to locate grantor and grantee td, then uses the grantee element to locate the value td
        Returns a list of all the data [grantor, grantee, value]
        """
        grantor = [content.string.strip() for content in spans[0].contents if content.string and content.string.strip()]
        grantee = [content.string.strip() for content in spans[1].contents if content.string and content.string.strip()]
        value = spans[1].parent.next_sibling.next_sibling.next_sibling.next_sibling.next_sibling.next_sibling.next_sibling.next_sibling.next_sibling.next_sibling
        return [grantor, grantee, value]
