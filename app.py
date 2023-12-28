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
            properties = Property.query.filter(Property.address.contains(property_address)).all()
        
        if owner_name:
            owners = Owner.query.filter(Owner.full_name.contains(owner_name)).all()
        
        return render_template('search_results.html',
                                form=form, 
                                owners=owners, 
                                properties=properties)
    
    # Initial GET render
    return render_template('home.html', 
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

@app.route('/search/properties')
def get_all_properties():
    """
    View function that retrieves all properties in the database and returns jsonified list.
    Returns: {"properties" : [{id, address, owner_id, company_id}, ...]}
    """
    all_properties = [property.serialize() for property in Property.query.all()]
    return jsonify(properties=all_properties)


@app.route('/search/companies')
def get_all_companies():
    """
    View function that retrieves all properties in the database and returns jsonified list.
    Returns: {"companies" : [{id, owner_id, owner_name, company_id, llc_name}, ...]} 
    """
    all_owner_company = [ownercompany.serialize() for ownercompany in OwnerCompany.query.all()]
    return jsonify("companies", all_owner_company)


@app.route('/search/owners')
def get_all_owners():
    """
    View Function that retrieves all owners in the database and returns jsonified list.
    Returns: {"owners" : [{id, full_name, address}, ...]}
    """
    all_owners = [owner.serialize() for owner in Owner.query.all()]
    return jsonify(owners=all_owners)


@app.route('/search/owners/<int:id>')
def get_owner(id):
    """
    View function that retieves an owner based on id from the database and returns jsonified data
    Returns: {"owner" : {id, full_name, address, *llc_name, *property_count, *properties}}
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
    # Using sqlalchemy's func object we can count the number of unique properties that share an owner id.
    property_count = db.session.query(func.count(Property.id)).filter(Property.owner_id == id).scalar()
    # CASE: the owner should always have one piece of property associated, 
    # Otherwise there was a scrapper error and the database's integrity is in question.
    if property_count > 0:
        owner_dict['property_count'] = property_count
        # Adds list of property addresses owned by owner to the dict
        properties = [property.address for property in Owner.query.get(id).properties]
        owner_dict['properties'] = properties
    
    return jsonify(owner=owner_dict)

if __name__ == '__main__':
    app.run(debug=True)