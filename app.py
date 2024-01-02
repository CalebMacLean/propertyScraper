from flask import Flask, render_template, flash, redirect, request, jsonify
from modules import Property, Owner, Company, OwnerCompany, connect_db, db
from forms import SearchForm
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

@app.route('/', methods=['GET', 'POST'])
def home():
    # GET Behaviors
    # Form Search Form created in forms.py
    form = SearchForm()
    # Query to database that finds the top 10 owners with the most property.
    landlords = (db.session.query(Owner.id, Owner.full_name, func.count(Property.id).label('property_count'))
                .join(Property)
                .group_by(Owner.id)
                .order_by(func.count(Property.id).desc())
                .limit(10))
    
    # POST Behaviors
    if form.validate_on_submit():
        # Variables containing form values
        owner_name = form.name.data.upper()
        property_address = form.property.data.upper()

        properties = None
        owners = None
        # Conditional making sure one of the fields was filled out.
        if property_address:
            properties = Property.query.filter(Property.address.contains(property_address)).limit(10).all()
        
        if owner_name:
            owners = Owner.query.filter(Owner.full_name.contains(owner_name)).limit(10).all()
        
        return render_template('search_results.html',
                                form=form, 
                                owners=owners, 
                                properties=properties)
    
    # Initial GET render
    return render_template('copy.html', 
                           form=form, 
                           landlords=landlords)

@app.route('/owner/<int:owner_id>')
def owner_info(owner_id):
    try:
        # Query the database for the owner with the given id
        owner = Owner.query.get_or_404(owner_id)
        # Query the database to find the amount of properties an owner owns
        property_count = db.session.query(func.count(Property.id)).filter(Property.owner_id == owner_id).scalar()
        # Query the database to find if there is a company associated with this owner
        company_id = db.session.query(OwnerCompany.company_id).filter(OwnerCompany.owner_id == owner_id).scalar()
        # Not all owners have companies, but if they do render html with company variable.
        if company_id:
            # Gets Company from database if their is a company id
            company = Company.query.get_or_404(company_id)
        else:
            # Sets company to none if no company
            company = None
        # Render the owner.html template with the owner
        return render_template('owner.html', 
                               owner=owner,
                               property_count=property_count, 
                               company=company)
    
    except Exception as e:
        error = e
        return render_template('error.html', error=error)
    
# #########################################################
# RESTFUL JSON API
# #########################################################
    
# API HELPER FUCTIONS
def paginate_by_page(model, page):
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
    paginated_dict = paginate_by_page(Property, page_id)
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
    paginated_dict = paginate_by_page(OwnerCompany, page_id)
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
    paginated_dict = paginate_by_page(Owner, page_id)
    # Return JSON if pagination query was successful
    if paginated_dict:
        return jsonify(owners=paginated_dict["items"], 
                       page_nav=paginated_dict["page_nav"])
    # Else return None
    return None


@app.route('/api/owners/<int:id>')
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

if __name__ == '__main__':
    app.run(debug=True)