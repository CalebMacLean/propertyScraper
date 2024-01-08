from flask import Flask, render_template, flash, redirect, request, jsonify
from modules import Property, Owner, Company, OwnerCompany, connect_db, db
from admin import SECRET_KEY, DATABASE_URI
from sqlalchemy import func
import os

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', DATABASE_URI)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['SECRET_KEY'] = SECRET_KEY

app.app_context().push()
connect_db(app)
db.create_all()

@app.route('/')
def home():
    
    return render_template('index.html')
    
# #########################################################
# RESTFUL JSON API
# #########################################################
    
# API HELPER FUCTIONS
def paginate_table_by_page(model, page):
    """
    Creates a Flask-SQLAlchemy pagination obj based off of an existing Database Model and page.
    Parameters:
    model (Flask-SQLAlchemy Model Obj) : Must be a model used in the application's database.
    page (int) : Must be a valid page number within the max range.
    Returns:
    Dictionary : {"items":[{dict}], "page_nav":{dict}}
    Null : None
    """
    # Try to create pagination object based off the page_id given
    try:
        pag_obj = model.query.paginate(page=page, per_page=10)
    # pag_obj will raise a 404 exception if page exceeds the max pages in the pagination object
    except:
        # Will set pag_obj to None for ease of conditional
        pag_obj = None
    # In cases where the pagination object didn't raise a 404, we will return the jsonified list of property dicts.
    if not(pag_obj == None):
        # Create dictionary that stores adjacent page_id values
        page_nav = {"prev_page":None, "next_page":None}
        # Calculate prev_page val if exsits
        if(pag_obj.has_prev):
            page_nav['prev_page'] = page - 1
        # Calculate next_page val if exists
        if(pag_obj.has_next):
            page_nav['next_page'] = page + 1
        # Create list of query items as dictionaries   
        items_list = [item.serialize() for item in pag_obj.items]
        # return dictionary of items_list and page_nav
        return {"items":items_list, "page_nav":page_nav}
    # Else return None
    return None

@app.route('/api/properties/<int:page_id>')
def get_all_properties(page_id):
    """
    View function that retrieves all properties in the database and returns jsonified list.
    Returns: 
    hasResults (JSON) : "{"properties" : [{id, address, owner_id, company_id}, ...], "page_nav" : {prev_page, next_page}}"
    noResults (Null) : None
    """
    paginated_dict = paginate_table_by_page(Property, page_id)
    # Return JSON if pagination query was successful
    if paginated_dict:
        return jsonify(properties=paginated_dict["items"], 
                       page_nav=paginated_dict["page_nav"])
    # Else return None
    return None


@app.route('/api/companies/<int:page_id>')
def get_all_companies(page_id):
    """
    View function that retrieves all properties in the database and returns jsonified list.
    Returns: {"companies" : [{id, owner_id, owner_name, company_id, llc_name}, ...], "page_nav" : {prev_page, next_page}} 
    """
    paginated_dict = paginate_table_by_page(OwnerCompany, page_id)
    # Return JSON if pagination query was successful
    if paginated_dict:
        return jsonify(companies=paginated_dict["items"], 
                       page_nav=paginated_dict["page_nav"])
    # Else return None
    return None


@app.route('/api/owners/<int:page_id>')
def get_all_owners(page_id):
    """
    View Function that retrieves all owners in the database and returns jsonified list.
    Returns: {"owners" : [{id, full_name, address}, ...], "page_nav" : {prev_page, next_page}}
    """
    paginated_dict = paginate_table_by_page(Owner, page_id)
    # Return JSON if pagination query was successful
    if paginated_dict:
        return jsonify(owners=paginated_dict["items"], 
                       page_nav=paginated_dict["page_nav"])
    # Else return None
    return None


@app.route('/api/owner/<int:id>')
def get_owner(id):
    """
    View function that retieves an owner based on id from the database and returns jsonified data
    Returns: {"owner" : {id, full_name, address, *llc_name, *property_count, *[properties]}}
    """
    def has_company(owner_id):
        """Helper Function, checks to see if the owner has an associated llc"""
        result = OwnerCompany.query.get(owner_id)
        if result == None:
            return False
        return True
    
    try:
        # TRY CASE: get owner instance by id
        owner = Owner.query.get_or_404(id)
    except Exception as e:
        # EXCEPT CASE: return jsonified error data. 
        return (jsonify(exceptions={"exception" : e}), 404)
    # TRY CASE SUCCEEDS
    # Create jsonifiable dict containing owner data
    owner_dict = owner.serialize()
    # CASE: owner has an llc, llc name added to the owner_dict
    if has_company(id):
        company_dict = OwnerCompany.query.get(id).serialize()
        owner_dict['llc_name'] = company_dict.llc_name
    else:
        owner_dict['llc_name'] = None
    # Using sqlalchemy's func object we can count the number of unique properties that share an owner id.
    property_count = db.session.query(func.count(Property.id)).filter(Property.owner_id == id).scalar()
    # CASE: the owner should always have one piece of property associated, 
    # Otherwise there was a scrapper error and the database's integrity is in question.
    
    owner_dict['property_count'] = property_count
    # Adds list of property addresses owned by owner to the dict
    properties = [property.address for property in Owner.query.get(id).properties]
    owner_dict['properties'] = properties
    
    return jsonify(owner=owner_dict)

@app.route('/api/owners/most')
def get_top_owners():
    """
    Retrieves owners with the most properties from the data base and returns them in JSON.
    Return:
    JSON : {"owners" : [{id, full_name, property_count}, ...]}
    """
    q = (db.session.query(Owner.id, Owner.full_name, func.count(Property.id).label('property_count'))
                .join(Property)
                .group_by(Owner.id)
                .order_by(func.count(Property.id).desc())
                .limit(10))
    owners = [{"id": o.id, "full_name": o.full_name, "property_count": o.property_count} for o in q]
    return jsonify(owners=owners)

@app.route('/api/search')
def search_all_tables():
    """
    Retrieves likely results from all database tables based on query val and returns JSON
    Parameters:
    - q (str) : search val
    Returns:
    - JSON : {"owners": [{id, full_name, address},..], "properties": [{id, address, owner_id, company_id},...],, "companies": [{id, llc_name, owner_id}]}
    """
    # get query val
    q = request.args.get('query', '')
    # query result variables
    q_owner = Owner.query.filter(Owner.full_name.contains(q)).limit(10).all()
    q_property = Property.query.filter(Property.address.contains(q)).limit(10).all()
    # Output of this query is [(<Company>, <OwnerCompany>),...]
    # Flaw of Database Schema is Company should rework that to be streamlined for queries
    q_company = db.session.query(Company, OwnerCompany).join(OwnerCompany, OwnerCompany.company_id == Company.id).filter(Company.llc_name.contains(q)).all()

    # serialized element lists determined by query variables finding results
    if q_owner:
        owners = [o.serialize() for o in q_owner]
    else:
        owners = None
    if q_property:
        properties = [p.serialize() for p in q_property]
    else:
        properties = None
    if q_company:
        # Using last query we can create a list of OwnerCompany instances which is more useful than a Company instance
        q_owner_company = [tuple[1] for tuple in q_company]
        companies = [c.serialize() for c in q_owner_company]
    else:
        companies = None
    # return the jsonified list in their respective sections
    return jsonify(owners=owners, properties=properties, companies=companies)

if __name__ == '__main__':
    app.run(debug=True)