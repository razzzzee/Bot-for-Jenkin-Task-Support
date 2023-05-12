from lxml import etree

def fetch_value_by_xpath(xml_payload, xpath):
    root = etree.XML(xml_payload)
    response = root.xpath(xpath)
    return response