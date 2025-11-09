import pandas as pd

#Load Excel files

cryptos_df = pd.read_excel("cryptos.xlsx")        # Column:  'cryptocurrencie'
exchanges_df = pd.read_excel("exchanges.xlsx")    # Column:  'exchanges'
influencers_df = pd.read_excel("influencers.xlsx") # Column:  'influencer'

#Function to create a dictionary from an Excel column

def create_entity_dict(df, column_name):
    """
    Converts an Excel column of type "Name (var1, var2, ...)" into a dictionary
    {Name: [Name, var1, var2, ...]}

    """
    entity_dict = {}
    for row in df[column_name].dropna():
        if '(' in row and ')' in row:
            name, variants_str = row.split('(', 1)
            name = name.strip()
            variants = [v.strip() for v in variants_str.rstrip(')').split(',')]
            variants.insert(0, name)
        else:
            name = row.strip()
            variants = [name]
        entity_dict[name] = variants
    return entity_dict

# Create dictionaries for each entity type

crypto_dict = create_entity_dict(cryptos_df, 'cryptocurrencie')
exchange_dict = create_entity_dict(exchanges_df, 'exchanges')
influencer_dict = create_entity_dict(influencers_df, 'influencer')

# Global dictionary

all_entities = {
    'cryptos': crypto_dict,
    'exchanges': exchange_dict,
    'influencers': influencer_dict
}

