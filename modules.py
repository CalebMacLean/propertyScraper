# Imports
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Configurations
db = SQLAlchemy()

def connect_db(app):
    """Connects an application to a database"""
    db.app = app
    db.init_app(app)


# Models
class Owner(db.Model):
    """Owner Model"""
    __tablename__ = 'owner'

    # Columns
    id = db.Column(db.Integer, primary_key=True,
                               autoincrement=True)
    full_name = db.Column(db.String(50), nullable=False)
    address = db.Column(db.String(100), nullable=False,
                                        unique=True)
    
    def serialize(self):
        """Returns dictionary representation of an owner instance that can be turned into JSON"""
        return {
            "id" : self.id,
            "full_name" : self.full_name,
            "address" : self.address
        }


class Company(db.Model):
    """LLC Model"""
    __tablename__ = 'company'
    
    # Columns
    id = db.Column(db.Integer, primary_key=True,
                                autoincrement=True)
    llc_name = db.Column(db.String(50), nullable=False,
                                        unique=True)


class OwnerCompany(db.Model):
    """OwnerCompany Model"""
    __tablename__ = 'owner_company'

    # Columns
    id = db.Column(db.Integer, primary_key=True,
                               autoincrement=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('owner.id'),
                                     nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'),
                                       nullable=False)
    
    # Relationships
    owner = db.relationship('Owner', backref='owner_companies', foreign_keys=[owner_id])
    company = db.relationship('Company', backref='owner_companies', foreign_keys=[company_id])

    # Unique Constraints
    __table_args__ = (db.UniqueConstraint('owner_id', 'company_id', name='uix_owner_company'),)

    def serialize(self):
        """Returns dictionary representation of an owner_company instance that can be turned into JSON"""
        return {
            "id" : self.id,
            "owner_id" : self.owner_id,
            "owner_name" : self.owner.full_name,
            "company_id" : self.company_id,
            "llc_name" : self.company.llc_name
        }


class Property(db.Model):
    """Property Model"""
    __tablename__ = 'property'

    # Columns
    id = db.Column(db.Integer, primary_key=True,
                                autoincrement=True)
    address = db.Column(db.String(100), nullable=False,
                                        unique=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('owner.id'))
    llc_id = db.Column(db.Integer, db.ForeignKey('company.id'))

    # Relationships
    company = db.relationship('Company', backref='properties', foreign_keys=[llc_id])
    owner = db.relationship('Owner', backref='properties', foreign_keys=[owner_id])

    def serialize(self):
        """Returns dictionary representation of an company instance that can be turned into JSON"""
        return {
            "id" : self.id,
            "address" : self.address,
            "owner_id" : self.owner_id,
            "llc_id" : self.llc_id,
        }


# Meta Data
class CrawlerProgress(db.Model):
    """CrawlerProgress Model"""
    __tablename__= 'crealer_progress'

    # Columns
    id = db.Column(db.Integer, primary_key=True,
                               autoincrement=True)
    time_started = db.Column(db.DateTime, nullable=False,
                                          default=datetime.utcnow)
    curr_url = db.Column(db.String(500), nullable=False)
    next_url = db.Column(db.String(500), nullable=False)
