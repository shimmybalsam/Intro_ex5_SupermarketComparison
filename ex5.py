import xml.etree.ElementTree as ET


def get_attribute(store_db, ItemCode, tag):
    '''Returns the attribute (tag)
    of an Item with code: Itemcode in the given store'''
    for key in store_db:
        if ItemCode == key:
            for inner_key in store_db[key]:
                if inner_key ==tag:
                    return store_db[key][tag]


def string_item(item):
    '''Textual representation of an item in a store.
    Returns a string in the format of '[ItemCode] (ItemName)' '''
    EMPTY_NOTE = ""
    iCode = EMPTY_NOTE
    iName = EMPTY_NOTE
    for key in item:
        if key == "ItemName":
            iName = item[key]
        elif key == "ItemCode":
            iCode = item[key]
    return "["+iCode+"]"+"\t{"+iName+"}"


def string_store_items(store_db):
    '''
    Textual representation of a store.
    Returns a string in the format of:
    string representation of item1
    string representation of item2
    '''
    EMPTY_NOTE = ""
    final_string = EMPTY_NOTE
    if len(store_db) == 0:
        return final_string
    for key in store_db:
        final_string += string_item(store_db[key]) + "\n"
    return final_string


def read_prices_file(filename):
    '''
    Read a file of item prices into a dictionary.  The file is assumed to
    be in the standard XML format of "misrad haclcala".
    Returns a tuple: store_id and a store_db, 
    where the first variable is the store name
    and the second is a dictionary describing the store. 
    The keys in this db will be ItemCodes of the different items and the
    values smaller  dictionaries mapping attribute names to their values.
    Important attributes include 'ItemCode', 'ItemName', and 'ItemPrice'
    '''
    tree = ET.parse(filename)
    root = tree.getroot()
    store_db = {}
    store_id = root.find("StoreId").text
    for element in root.find("Items"):
        if element.tag == "Item":
            temp_dict = {}
            for parameter in element:
                temp_dict[parameter.tag] = parameter.text
        store_db[temp_dict["ItemCode"]] = temp_dict
    return (store_id, store_db)


def filter_store(store_db, filter_txt):
    '''
    Create a new dictionary that includes only the items 
    that were filtered by user.
    I.e. items that text given by the user is part of their ItemName. 
    Args:
    store_db: a dictionary of dictionaries as created in read_prices_file.
    filter_txt: the filter text as given by the user.
    '''
    filtered_db = {}
    for key, val in store_db.items():
        if filter_txt in store_db[key]["ItemName"]:
            filtered_db[key] = val
    return filtered_db

def create_basket_from_txt(basket_txt): 
    '''
    Receives text representation of few items (and maybe some garbage 
      at the edges)
    Returns a basket- list of ItemCodes that were included in basket_txt
    '''
    basket = []
    for i in basket_txt.split():
        if "[" in i and "]" in i:
            basket.append(i[1:len(i)-1])
    return basket


def get_basket_prices(store_db, basket):
    '''
    Arguments: a store - dictionary of dictionaries and a basket - 
       a list of ItemCodes
    Go over all the items in the basket and create a new list 
      that describes the prices of store items
    In case one of the items is not part of the store, 
      its price will be None.
    '''
    prices_list = []
    item_in_list = False
    for code in range(len(basket)):
        for key in store_db:
            if basket[code] not in store_db:
                item_in_list = False
                continue
            elif basket[code] == key:
                prices_list.append(float(store_db[key]["ItemPrice"]))
                item_in_list = True
        if not item_in_list:
            prices_list.append(None)
    return prices_list


def sum_basket(price_list):
    '''
    Receives a list of prices
    Returns a tuple - the sum of the list (when ignoring Nones) 
      and the number of missing items (Number of Nones)
    '''
    sum_price_list = 0
    missing_items = 0
    for price in range(len(price_list)):
        if price_list[price] == None:
            missing_items +=1
        else:
            sum_price_list += price_list[price]
    return (sum_price_list, missing_items)

 
def basket_item_name(stores_db_list, ItemCode): 
    ''' 
    stores_db_list is a list of stores (list of dictionaries of 
      dictionaries)
    Find the first store in the list that contains the item and return its
    string representation (as in string_item())
    If the item is not avaiable in any of the stores return only [ItemCode]
    '''
    for store in stores_db_list:
        for key in store:
            if ItemCode == key:
                return string_item(store[key])
    return "[" + ItemCode + "]"


def save_basket(basket, filename):
    ''' 
    Save the basket into a file
    The basket reresentation in the file will be in the following format:
    [ItemCode1] 
    [ItemCode2] 
    ...
    [ItemCodeN]
    '''
    with open(filename, 'w') as saved_basket:
        for item in basket:
            saved_basket.write("[" + item + "]" + "\n")


def load_basket(filename):
    ''' 
    Create basket (list of ItemCodes) from the given file.
    The file is assumed to be in the format of:
    [ItemCode1] 
    [ItemCode2] 
    ...
    [ItemCodeN]
    '''
    with open(filename, 'r') as saved_basket:
        new_basket = saved_basket.readlines()
        for item in range(len(new_basket)):
            new_basket[item] = new_basket[item][1:len(new_basket[item])-2]
        return new_basket


def best_basket(list_of_price_list):
    '''
    Arg: list of lists, where each inner list is list of prices as created
    by get_basket_prices.
    Returns the cheapest store (index of the cheapest list) given that a 
    missing item has a price of its maximal price in the other stores *1.2
    '''
    sums = []
    temp_min_sum = 0
    min_index = 0
    FINE = 1.25
    for inner_list in range(len(list_of_price_list)):
        sums.append(0) #creates per list of prices a new object in sums list
        for price in range(len(list_of_price_list[inner_list])):
            if list_of_price_list[inner_list][price] != None:
                # add's to said object in sums list the price listed
                # in the inner_list index
                sums[inner_list] += list_of_price_list[inner_list][price]
            else:
                # if the price is 'None', finds the most expensive price of the
                # same product in the other prices lists, and fines the product
                # of the original list by 125% of the most expensive price.
                temp_max = 0
                for index in range(len(list_of_price_list)):
                    element = list_of_price_list[index][price]
                    if element != None and element > temp_max:
                        temp_max = element
                # Once fined, that extra expensive price will be added to the
                # product's worth in the sums list
                sums[inner_list] += (temp_max*FINE)
        if temp_min_sum == 0:
            temp_min_sum = inner_list
            min_index = inner_list
        elif sums[inner_list] < temp_min_sum:
            temp_min_sum = sums[inner_list]
            min_index = inner_list
    return min_index