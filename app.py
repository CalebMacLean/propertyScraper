from flask import Flask, render_template, flash, redirect, request, get_flashed_messages
from modules import Property, Owner, Company, OwnerCompany, connect_db, db
from forms import SearchForm
from sqlalchemy import func
import os

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'postgresql:///washoe_properties')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['SECRET_KEY'] = "1Kn0w@53cr3t"

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
    

if __name__ == '__main__':
    app.run(debug=True)