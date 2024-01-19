# Imports
import os
import time
from flask import Flask
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from modules import Owner, Company, Property, OwnerCompany, CrawlerProgress, connect_db, db
from scraper import scraper

# Configurations
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'postgresql:///washoe_properties')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'P@55w0rdI5S3cr3t')

app.app_context().push()
connect_db(app)
db.create_all()

# Global Variables
starting_url = None
max_id = db.session.query(func.max(CrawlerProgress.id)).scalar()
if max_id:
    crawler_progress = CrawlerProgress.query.filter(CrawlerProgress.id == max_id).first()
    starting_url = crawler_progress.next_url
else:
    starting_url = 'https://www.washoecounty.gov/assessor/cama/?parid=00102001'


# Database Functions
def get_or_insert_owner(name, address):
    """
    Will attempt to insert a new owner instance to the owner table if the owner isn't in the database
    and either way will return an owner result obj.
    
    Parameters:
    - name (str) : Full name of Owner.
    - address (str) : Owner's address.

    Return:
    - Owner (ResultObj) : Object containing the id, full_name and address values of an Owner instance.
    """
    try:
        # Instantiate Owner using parameters
        owner = Owner(full_name = name,
                      address = address)
        print(f"owner: {owner}")
        db.session.add(owner)
        db.session.commit()

    except IntegrityError:
        # An IntegrityError will occur if the Owner instantiation has a non-unique address value.
        # This will rollback the error in the session.
        db.session.rollback()

    finally:
        # Returns a owner instance based on the address parameter.
        return Owner.query.filter_by(address=address).first()
    
def get_or_insert_company(name):
    """
    Will attempt to insert a new company instance to the company table if the name is unique, either
    way it will return the company instances.

    Parameters:
    - name (str) : Name of LLC
    
    Return:
    - Company (ResultObj) : Object containing the id, name values of the Company instance.
    """
    try:
        company = Company(llc_name = name)
        db.session.add(company)
        db.session.commit()
    
    except IntegrityError:
        # llc_name is a unique column, so an IntegrityError will raise if the name is already in the db
        db.session.rollback()
    
    finally:
        # Returns a company instance based on the name parameter.
        return Company.query.filter_by(llc_name=name).first()


def update_database(data, url):
    # First update metadata table
    # print(f"Grantor: {data['grantor']}")
    # print(f"Price: {data['price']}")
    try:
        progress = CrawlerProgress(curr_url=url, next_url=data['next_url'])
        db.session.add(progress)
        db.session.commit()

    except Exception as e:
        print(f"Exception from update_database : {e}")

    # Case: Owner is an LLC
    if ('LLC' in data['owner_name']):
        print('Case: Owner is LLC')
        company = get_or_insert_company(name=data['owner_name'])

        # SubCase: Owner of LLC was the prev grantor
        if int(data['price']) == 0:
            # print('Owner of LLC was the prev grantor')
            owner = get_or_insert_owner(name=data['grantor'], address=data['owner_address'])
            # print(f'Owner: {owner}')
            # Try to update the owner_company table to make sure their is an association between person and company.
            try:
                owner_company = OwnerCompany(owner_id = owner.id, company_id = company.id)
                # print(f"owner_company: {owner_company}")
                db.session.add(owner_company)
                db.session.commit()

            except IntegrityError:
                # If pairing already exist IntegrityError raised
                db.session.rollback()

            # Try to insert property instance to property table 
            try:
                property = Property(address = data['property_address'], 
                                    owner_id = owner.id, 
                                    llc_id = company.id)
                print(f"property: {property}")
                db.session.add(property)
                db.session.commit()
            
            except Exception as e:
                db.session.rollback()
                print(f"Exception from update_database : {e}")
            
    # Case: Owner isn't an LLC
    elif not ('LLC' in data['owner_name']):
        # print('Case: Owner is not a LLC, should see this!')
        try:
            owner = get_or_insert_owner(name = data['owner_name'], address = data['owner_address'])
            property = Property(address = data['property_address'], owner_id = owner.id)
            print(f"property: {property}")
            # Don't have to add owner to the session because get_or_insert_owner will have dealt w/ it.
            db.session.add(property)
            db.session.commit()
        
        except Exception as e:
            db.session.rollback()
            print(f"Exception from update_database : {e}")

    # In all other cases
    else:
        print("Update Database did not work. Check Database CrawlerProgress table to see how far it got.")
        
# Crawler
def crawler(url, index=100):
    """
    Will crawl across the Washoe Assessor site scraping data from each url it crosses, the data will 
    be plugged into the database, and then will go to the next url until the idx is met.

    Parameters:
    - url (str) : URL from washoe site.
    - idx (int) : Integer that will determine how many times the loop is run, default is 100.

    Return:
    - Last URL (str) : Will return the last url reached.
    - Exception : any exceptions that arise.
    """
    # Conditionals to check if parameters meet requirements
    current_url = url
    loop_count = 0
    if not (isinstance(current_url, str)) and not ('https://www.washoecounty.gov/assessor/cama/?parid=' in current_url):
        raise TypeError('URL needs to be a string or needs to start with https://www.washoecounty.gov/assessor/cama/?parid=')
    if not (isinstance(index, int)):
        raise TypeError('Index must be an integer')

    # loop that crawls
    while loop_count < index:
        time.sleep(2)
        loop_count += 1
        data = scraper(current_url)

        if None in data.values():
            return ("Incomplete Scrape", current_url)
        
        if loop_count % 10 == 0:
            print(current_url)
        
        try:
            update_database(data, current_url)

        except Exception as e:
            print(f"Exception in Crawler: {e}")
            print(f"{current_url}")

        finally:
            current_url = data['next_url']
    
    return current_url

crawler(starting_url)