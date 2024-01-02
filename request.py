import requests
from lxml import etree

def element_to_dict_with_children(element):
    """
    Converts an element and all its children to a dictionary.

    Args:
        element: An element object.

    Returns:
        A dictionary representation of the element and all its children.
    """
    # If element has no children, return its text
    if not list(element):
        return element.text

    # Create a dictionary to hold the element and its children
    result = {}

    # Add the element's attributes to the dictionary
    if element.attrib:
        result.update(element.attrib)

    # Loop through the element's children
    for child in element:
        # Get the child's tag and value
        child_tag = child.tag.split('}')[1] if '}' in child.tag else child.tag
        child_value = element_to_dict_with_children(child)

        # If the tag already exists in the dictionary, convert the value to a list
        if child_tag in result:
            if isinstance(result[child_tag], list):
                result[child_tag].append(child_value)
            else:
                result[child_tag] = [result[child_tag], child_value]
        else:
            result[child_tag] = child_value

    return result



def parse_response(result_code, response_tag, root):
    result_code = root.find(f".//{result_code}").text
    if result_code != '0':
        print("Error: %s" % result_code)
    response_data = root.find(f".//{response_tag}")
    return response_data

def dict_to_xml(tag_name, item_name, items):
    xml_str = f'<{tag_name}>'
    for item in items:
        xml_str += f'<{item_name}>'
        for key, value in item.items():
            xml_str += f'<{key}>{value}</{key}>'
        xml_str += f'</{item_name}>'
    xml_str += f'</{tag_name}>'
    return xml_str


def get_template_file(filename=None):
    #filename="req2.xml"
    
    with open(filename, 'r') as file:
        template_file = file.read()
        return template_file

def get_request_object(tag=None):
    return {
        'headers': {'Content-Type': 'text/xml;charset=UTF-8'},
        'verify': False,
        #'url': 'http://10.4.104.87:41409/ERecharge/ERSUpdateDealerInfo'
        'url':'http://10.4.104.87:41409/ERecharge/ERSRegisterDealer'
        #'url': f'http://10.4.104.86:8193/Connector/GenericConnector?type={tag}'
        #'url': 'http://62.231.248.100:8193/Connector/GenericConnector?type=GETEVCHRCARD'
        #'url': 'http://62.231.248.100:8193/ERecharge/ERSBalanceEnquiryAdapter'
        #'url': 'http://10.4.109.28:41409/ERecharge/ERSProductEnquiry'
        #'url':'http://62.231.248.100:8193/ERecharge/ERSBalanceEnquiryAdapter?typeGETBALINFO'
    }
		

def fill_xml_tags_with_data(xml_str: str, data: dict):
    root = etree.fromstring(xml_str)
    for tag_name, value in data.items():
        for elem in root.iter(tag_name):
            elem.text = value
    return etree.tostring(root, pretty_print=True).decode()
	

#####################
def test(tag=None,filename=None,responseTag=None):
    request_object = get_request_object(tag)
    print("Request: ",request_object.get('url'))
    print("==============================")
    request_file = get_template_file(filename)
    print("Request: ",request_file)
    print("==================================")
    request = requests.post(data=request_file, **request_object)
    print("headers: ",request.headers)
    print("==============================")
    print("Request Content Type: ",request.headers.get("Content-Type", False) and str(request.headers.get("Content-Type", '')) )
    print("==============================")
    print(f"Response: {request.status_code}")
    print("==============================")
    if request.status_code == 200:
        response = bytes(request.text, 'utf-8')
        print(response)
        print("==============================")
        root = etree.fromstring(response)
        product_enquiry_response = parse_response(result_code="ResultCode", response_tag=responseTag, root=root)
        print("Parse: ",product_enquiry_response)
        print("========================")
        product_enquiry_response = element_to_dict_with_children(product_enquiry_response)
        for k,v in product_enquiry_response.items():
            if isinstance(v,bytes):
                product_enquiry_response[k] = v.decode('utf-8')
        print(product_enquiry_response)
        print("========================")
    else:
        print(f"Response: {request.text}")
        print("=========================")


print("Please enter the tag for the request: ")
tag = input()
print("please enter filename: ")
filename=input()
print("Please enter response Tag: ")
responseTag = input()
test(tag,filename,responseTag)
